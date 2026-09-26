from __future__ import annotations

import json
from typing import Any

import anthropic

from .models import (
    CascadeLevel,
    ModerationCategory,
    ModerationResult,
    estimate_cost,
    needs_review_result,
)

MODEL_IDS = {
    "haiku": "claude-haiku-4-5",
    "sonnet": "claude-sonnet-5",
}

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
        client: Any = None,
    ):
        """
        Args:
            api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var).
            default_model: "haiku", "sonnet", or a full model ID.
            enable_cache: Mark the system prompt with cache_control. Note: the
                built-in prompt (~300 tokens) is below the minimum cacheable
                prefix (4096 tokens on Haiku 4.5, 1024 on Sonnet 5), so the API
                silently skips caching unless you supply a longer prompt.
                Harmless either way; check `cache_read_input_tokens` to verify.
            client: Pre-built `anthropic.Anthropic` (or compatible) instance.
        """
        self._client = client or anthropic.Anthropic(api_key=api_key)
        self._default_model = default_model
        self._enable_cache = enable_cache

    def moderate(
        self,
        image_b64: str,
        media_type: str = "image/jpeg",
        model: str | None = None,
    ) -> ModerationResult:
        """Classify one image. Never raises on API/parse failures; returns a
        needs_review result instead."""
        model_key = model or self._default_model
        model_id = _resolve_model_id(model_key)
        level = _cascade_level(model_id)
        try:
            response = self._client.messages.create(
                **self._request_params(model_id, image_b64, media_type)
            )
        except anthropic.APIError as e:
            return needs_review_result(
                f"API error: {type(e).__name__}: {e}", resolved_at=level
            )
        return _build_result(response, level)

    def moderate_batch(
        self,
        images: list[tuple[str, str]],
        model: str | None = None,
    ) -> str:
        """Submit a batch of images for async moderation. Returns batch ID.

        Args:
            images: List of (image_b64, media_type) tuples. Result custom_ids
                are "img_<index>" in this list's order.
            model: Model key ("haiku" or "sonnet") or full model ID.

        Returns:
            Batch ID to poll with `get_batch_status` / `get_batch_results`.
        """
        model_id = _resolve_model_id(model or self._default_model)
        requests = [
            {
                "custom_id": f"img_{i}",
                "params": self._request_params(model_id, b64, mtype),
            }
            for i, (b64, mtype) in enumerate(images)
        ]
        batch = self._client.messages.batches.create(requests=requests)
        return batch.id

    def get_batch_status(self, batch_id: str) -> str:
        """Return the batch's processing_status ("in_progress", "canceling", "ended")."""
        return self._client.messages.batches.retrieve(batch_id).processing_status

    def get_batch_results(self, batch_id: str) -> list[ModerationResult]:
        """Retrieve results for an ended batch, one per submitted image.

        Every entry is returned - errored/expired/canceled requests become
        needs_review results - with its custom_id in `details["custom_id"]`.
        Results are sorted back into submission order.
        """
        results = []
        for entry in self._client.messages.batches.results(batch_id):
            rtype = entry.result.type
            if rtype == "succeeded":
                msg = entry.result.message
                result = _build_result(
                    msg, _cascade_level(getattr(msg, "model", "")), batch=True
                )
            else:
                error = getattr(entry.result, "error", None)
                result = needs_review_result(
                    f"Batch request {rtype}" + (f": {error}" if error else ""),
                    batch_result_type=rtype,
                )
            result.details["custom_id"] = entry.custom_id
            results.append(result)
        results.sort(key=lambda r: _custom_id_order(r.details["custom_id"]))
        return results

    def _request_params(self, model_id: str, image_b64: str, media_type: str) -> dict:
        system_block = {"type": "text", "text": MODERATION_SYSTEM_PROMPT}
        if self._enable_cache:
            system_block["cache_control"] = {"type": "ephemeral"}
        params = {
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
                                "media_type": media_type,
                                "data": image_b64,
                            },
                        },
                        {"type": "text", "text": "Classify this image."},
                    ],
                }
            ],
        }
        # Sonnet 5 runs adaptive thinking when `thinking` is omitted; a short
        # JSON classification doesn't need it and it would eat the 100-token cap.
        if "sonnet-5" in model_id:
            params["thinking"] = {"type": "disabled"}
        return params


def _resolve_model_id(key: str) -> str:
    return MODEL_IDS.get(key, key)


def _cascade_level(model_id: str) -> CascadeLevel:
    return CascadeLevel.HAIKU if "haiku" in model_id else CascadeLevel.SONNET


def _custom_id_order(custom_id: str) -> tuple:
    prefix, _, idx = custom_id.rpartition("_")
    return (0, int(idx), "") if idx.isdigit() else (1, 0, custom_id)


def _build_result(
    message: Any, level: CascadeLevel, batch: bool = False
) -> ModerationResult:
    """Turn a Messages API response into a ModerationResult (never raises)."""
    usage = getattr(message, "usage", None)
    input_tokens = getattr(usage, "input_tokens", 0) or 0
    output_tokens = getattr(usage, "output_tokens", 0) or 0
    cache_read = getattr(usage, "cache_read_input_tokens", 0) or 0
    cache_write = getattr(usage, "cache_creation_input_tokens", 0) or 0
    stop_reason = getattr(message, "stop_reason", None)

    text = "".join(
        getattr(b, "text", "")
        for b in (getattr(message, "content", None) or [])
        if getattr(b, "type", None) == "text"
    )

    if stop_reason == "refusal":
        result = needs_review_result("Model refused to classify", resolved_at=level)
    elif not text.strip():
        result = needs_review_result(
            f"No text in response (stop_reason={stop_reason})", resolved_at=level
        )
    else:
        parsed = _parse_response(text)
        if parsed is None:
            result = needs_review_result(
                f"Failed to parse: {text[:100]}", resolved_at=level
            )
        else:
            result = ModerationResult(
                safe=parsed["safe"],
                category=parsed["category"],
                confidence=parsed["confidence"],
                resolved_at=level,
                details={"reason": parsed["reason"]},
            )

    result.input_tokens = input_tokens
    result.output_tokens = output_tokens
    result.cached_tokens = cache_read
    result.cache_creation_tokens = cache_write
    result.estimated_cost = estimate_cost(
        level.value, input_tokens, output_tokens, cache_read, cache_write, batch=batch
    )
    result.details["stop_reason"] = stop_reason
    return result


def _parse_response(text: str) -> dict | None:
    """Parse the model's JSON verdict. Returns None if it isn't a usable object.

    Unknown categories map to "other"; confidence is clamped to [0, 1].
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[-1].rsplit("```", 1)[0]
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    if not isinstance(data, dict) or not isinstance(data.get("safe"), bool):
        return None

    safe = data["safe"]
    category = ModerationCategory.parse(
        data.get("category", "safe" if safe else "other")
    )
    try:
        confidence = min(1.0, max(0.0, float(data.get("confidence", 0.0))))
    except (TypeError, ValueError):
        confidence = 0.0
    return {
        "safe": safe,
        "category": category,
        "confidence": confidence,
        "reason": str(data.get("reason", "")),
    }
