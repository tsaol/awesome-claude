"""Main moderation pipeline orchestrating the tiered cascade."""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from .client import ClaudeModerationClient
from .models import CascadeLevel, ModerationResult, needs_review_result
from .prefilter import PHashFilter
from .preprocessing import preprocess_image

VALID_LEVELS = ("phash", "haiku", "sonnet")
LEVEL_ALIASES = {"prefilter": "phash"}


class ImageModerationPipeline:
    """Cost-optimized image moderation through a tiered cascade.

    Cascade order:
        1. pHash lookup against known-violation database (zero cost)
        2. Claude Haiku with resized image (low cost)
        3. Claude Sonnet for low-confidence or undetermined Haiku results

    If no level can decide (no match and no model level enabled, or every
    model call failed), the result has needs_review=True and safe=False.
    """

    def __init__(
        self,
        anthropic_api_key: str | None = None,
        hash_db_path: str | Path | None = None,
        enable_cache: bool = True,
        max_image_size: int = 768,
        image_quality: int = 75,
        sonnet_threshold: float = 0.7,
        cascade_levels: list[str] | None = None,
        client: Any = None,
    ):
        """
        Args:
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var).
            hash_db_path: Path to CSV of known-violation perceptual hashes.
            enable_cache: Mark the system prompt with cache_control. Only takes
                effect if the prompt exceeds the model's minimum cacheable size
                (the built-in prompt does not); see ClaudeModerationClient.
            max_image_size: Max dimension for image resizing.
            image_quality: JPEG compression quality (1-100).
            sonnet_threshold: If Haiku confidence is below this (for any
                verdict, safe or not), escalate to Sonnet.
            cascade_levels: Which levels to enable: "phash" (alias
                "prefilter"), "haiku", "sonnet". Default: all.
            client: Optional pre-built `anthropic.Anthropic`-compatible client.
        """
        self._max_size = max_image_size
        self._quality = image_quality
        self._sonnet_threshold = sonnet_threshold

        levels = _normalize_levels(cascade_levels)
        self._use_phash = "phash" in levels
        self._use_haiku = "haiku" in levels
        self._use_sonnet = "sonnet" in levels

        self._phash_filter = PHashFilter(hash_db_path) if self._use_phash else None

        if self._use_haiku or self._use_sonnet:
            self._client = ClaudeModerationClient(
                api_key=anthropic_api_key,
                default_model="haiku" if self._use_haiku else "sonnet",
                enable_cache=enable_cache,
                client=client,
            )
        else:
            self._client = None

        self._stats = {
            "total": 0,
            "resolved_at": {level.value: 0 for level in CascadeLevel},
            "needs_review": 0,
            "escalated": 0,
            "total_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cached_tokens": 0,
            "total_cache_creation_tokens": 0,
        }

    def moderate(self, image_source: str | bytes | Path) -> ModerationResult:
        """Run the full cascade on a single image."""
        self._stats["total"] += 1

        # Level 1: pHash lookup
        if self._use_phash and self._phash_filter:
            result = self._phash_filter.check(image_source)
            if result is not None:
                return self._record(result)

        if self._client is None:
            return self._record(
                needs_review_result(
                    "No pHash match and no model level enabled; not moderated"
                )
            )

        # Preprocess for Claude
        b64, meta = preprocess_image(
            image_source,
            max_size=self._max_size,
            quality=self._quality,
        )

        haiku_result = None
        # Level 2: Haiku
        if self._use_haiku:
            haiku_result = self._client.moderate(b64, model="haiku")
            needs_escalation = self._use_sonnet and (
                haiku_result.needs_review
                or haiku_result.confidence < self._sonnet_threshold
            )
            if not needs_escalation:
                haiku_result.details["preprocessing"] = meta
                return self._record(haiku_result)
            # Haiku's tokens were spent even though Sonnet makes the call.
            self._add_usage(haiku_result)
            self._stats["escalated"] += 1

        # Level 3: Sonnet (escalation, or the only model level)
        result = self._client.moderate(b64, model="sonnet")
        result.details["preprocessing"] = meta
        if haiku_result is not None:
            result.details["escalated"] = True
            result.details["haiku_result"] = {
                "safe": haiku_result.safe,
                "category": haiku_result.category.value,
                "confidence": haiku_result.confidence,
                "needs_review": haiku_result.needs_review,
                "estimated_cost": haiku_result.estimated_cost,
            }
        return self._record(result)

    def moderate_batch_async(
        self, image_sources: list[str | bytes | Path]
    ) -> str:
        """Submit a batch of images for async moderation via Batch API.

        Uses a single model (Haiku if enabled, else Sonnet); there is no
        pHash or escalation step in batch mode. Returns a batch ID.
        """
        if self._client is None:
            raise ValueError(
                "Batch moderation requires a 'haiku' or 'sonnet' cascade level"
            )
        images = []
        for src in image_sources:
            b64, _ = preprocess_image(
                src, max_size=self._max_size, quality=self._quality
            )
            images.append((b64, "image/jpeg"))

        return self._client.moderate_batch(
            images, model="haiku" if self._use_haiku else "sonnet"
        )

    def get_batch_status(self, batch_id: str) -> str:
        """Return the batch's processing_status; results are ready at "ended"."""
        self._require_client()
        return self._client.get_batch_status(batch_id)

    def get_batch_results(self, batch_id: str) -> list[ModerationResult]:
        """Retrieve results of an ended batch (see ClaudeModerationClient)."""
        self._require_client()
        return self._client.get_batch_results(batch_id)

    @property
    def stats(self) -> dict:
        return copy.deepcopy(self._stats)

    def _require_client(self) -> None:
        if self._client is None:
            raise ValueError("No model level enabled")

    def _add_usage(self, result: ModerationResult) -> None:
        self._stats["total_cost"] += result.estimated_cost
        self._stats["total_input_tokens"] += result.input_tokens
        self._stats["total_output_tokens"] += result.output_tokens
        self._stats["total_cached_tokens"] += result.cached_tokens
        self._stats["total_cache_creation_tokens"] += result.cache_creation_tokens

    def _record(self, result: ModerationResult) -> ModerationResult:
        self._stats["resolved_at"][result.resolved_at.value] += 1
        if result.needs_review:
            self._stats["needs_review"] += 1
        self._add_usage(result)
        return result


def _normalize_levels(cascade_levels: list[str] | None) -> set[str]:
    if cascade_levels is None:
        return set(VALID_LEVELS)
    levels = set()
    for name in cascade_levels:
        name = LEVEL_ALIASES.get(name, name)
        if name not in VALID_LEVELS:
            raise ValueError(
                f"Unknown cascade level {name!r}; valid: "
                f"{', '.join(VALID_LEVELS)} (alias: prefilter -> phash)"
            )
        levels.add(name)
    if not levels:
        raise ValueError("cascade_levels must enable at least one level")
    return levels
