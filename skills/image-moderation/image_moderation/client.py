import json

import anthropic

from .models import (
    CascadeLevel,
    ModerationCategory,
    ModerationResult,
    estimate_cost,
)

MODERATION_SYSTEM_PROMPT = """\
You are an image content moderator. Analyze the provided image and classify it.

## Categories
- safe: No policy violations
- violence: Graphic violence, gore, or physical harm
- sexual: Sexually explicit or suggestive content
- hate: Hate speech, symbols, or discriminatory content
- self_harm: Self-harm or suicide-related content
- drugs: Illegal drug use or promotion
- weapons: Illegal weapons or instructions for harm
- spam: Spam, scams, or misleading content
- other: Other policy violations not covered above

## Rules
- Artistic/educational context may be safe even with sensitive themes
- Medical/scientific imagery is generally safe
- News/documentary content should be evaluated in context
- When uncertain, err on the side of flagging for review

## Output Format
Respond with ONLY a JSON object, no other text:
{"safe": bool, "category": string, "confidence": float 0-1, "reason": string (max 20 words)}
"""


class ClaudeModerationClient:
    def __init__(
        self,
        api_key: str | None = None,
        default_model: str = "haiku",
        enable_cache: bool = True,
    ):
        self._client = anthropic.Anthropic(api_key=api_key)
        self._default_model = default_model
        self._enable_cache = enable_cache

    def moderate(
        self,
        image_b64: str,
        media_type: str = "image/jpeg",
        model: str | None = None,
    ) -> ModerationResult:
        model_key = model or self._default_model
        model_id = _resolve_model_id(model_key)
        cascade_level = (
            CascadeLevel.HAIKU if "haiku" in model_id else CascadeLevel.SONNET
        )

        system_block = {
            "type": "text",
            "text": MODERATION_SYSTEM_PROMPT,
        }
        if self._enable_cache:
            system_block["cache_control"] = {"type": "ephemeral"}

        response = self._client.messages.create(
            model=model_id,
            max_tokens=100,
            system=[system_block],
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {
                            "type": "text",
                            "text": "Classify this image.",
                        },
                    ],
                }
            ],
        )

        parsed = _parse_response(response.content[0].text)
        usage = response.usage

        input_tokens = usage.input_tokens
        output_tokens = usage.output_tokens
        cached_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0

        return ModerationResult(
            safe=parsed["safe"],
            category=ModerationCategory(parsed["category"]),
            confidence=parsed["confidence"],
            resolved_at=cascade_level,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cached_tokens=cached_tokens,
            estimated_cost=estimate_cost(
                model_key, input_tokens, output_tokens, cached_tokens
            ),
            details={"reason": parsed.get("reason", "")},
        )

    def moderate_batch(
        self,
        images: list[tuple[str, str]],
        model: str | None = None,
    ) -> str:
        """Submit a batch of images for async moderation. Returns batch ID.

        Args:
            images: List of (image_b64, media_type) tuples.
            model: Model key ("haiku" or "sonnet").

        Returns:
            Batch ID to poll for results.
        """
        model_key = model or self._default_model
        model_id = _resolve_model_id(model_key)

        system_block = {
            "type": "text",
            "text": MODERATION_SYSTEM_PROMPT,
        }
        if self._enable_cache:
            system_block["cache_control"] = {"type": "ephemeral"}

        requests = []
        for i, (b64, mtype) in enumerate(images):
            requests.append({
                "custom_id": f"img_{i}",
                "params": {
                    "model": model_id,
                    "max_tokens": 100,
                    "system": [system_block],
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "image",
                                    "source": {
                                        "type": "base64",
                                        "media_type": mtype,
                                        "data": b64,
                                    },
                                },
                                {"type": "text", "text": "Classify this image."},
                            ],
                        }
                    ],
                },
            })

        batch = self._client.messages.batches.create(requests=requests)
        return batch.id

    def get_batch_results(self, batch_id: str) -> list[ModerationResult]:
        """Retrieve results for a completed batch."""
        results = []
        for entry in self._client.messages.batches.results(batch_id):
            if entry.result.type != "succeeded":
                continue
            msg = entry.result.message
            parsed = _parse_response(msg.content[0].text)
            usage = msg.usage
            input_tokens = usage.input_tokens
            output_tokens = usage.output_tokens
            cached_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0

            results.append(
                ModerationResult(
                    safe=parsed["safe"],
                    category=ModerationCategory(parsed["category"]),
                    confidence=parsed["confidence"],
                    resolved_at=CascadeLevel.HAIKU,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    cached_tokens=cached_tokens,
                    estimated_cost=estimate_cost(
                        "haiku", input_tokens, output_tokens, cached_tokens
                    ),
                    details={"reason": parsed.get("reason", "")},
                )
            )
        return results


def _resolve_model_id(key: str) -> str:
    models = {
        "haiku": "claude-haiku-4-5-20251001",
        "sonnet": "claude-sonnet-4-6-20260219",
    }
    return models.get(key, key)


def _parse_response(text: str) -> dict:
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        data = {
            "safe": False,
            "category": "other",
            "confidence": 0.0,
            "reason": f"Failed to parse: {text[:100]}",
        }

    data.setdefault("safe", False)
    data.setdefault("category", "other")
    data.setdefault("confidence", 0.0)
    return data
