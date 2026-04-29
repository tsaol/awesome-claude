"""Main moderation pipeline orchestrating the tiered cascade."""

from pathlib import Path

from .client import ClaudeModerationClient
from .models import CascadeLevel, ModerationCategory, ModerationResult
from .prefilter import PHashFilter
from .preprocessing import preprocess_image


class ImageModerationPipeline:
    """Cost-optimized image moderation through a tiered cascade.

    Cascade order:
        1. pHash lookup against known-violation database (zero cost)
        2. Claude Haiku with resized image (low cost)
        3. Claude Sonnet for uncertain results (higher cost, better accuracy)
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
    ):
        """
        Args:
            anthropic_api_key: Anthropic API key (or set ANTHROPIC_API_KEY env var).
            hash_db_path: Path to CSV of known-violation perceptual hashes.
            enable_cache: Enable prompt caching for system prompt.
            max_image_size: Max dimension for image resizing.
            image_quality: JPEG compression quality (1-100).
            sonnet_threshold: If Haiku confidence is below this, escalate to Sonnet.
            cascade_levels: Which levels to enable. Default: all.
        """
        self._max_size = max_image_size
        self._quality = image_quality
        self._sonnet_threshold = sonnet_threshold

        levels = set(cascade_levels or ["phash", "haiku", "sonnet"])
        self._use_phash = "phash" in levels
        self._use_haiku = "haiku" in levels
        self._use_sonnet = "sonnet" in levels

        self._phash_filter = PHashFilter(hash_db_path) if self._use_phash else None

        if self._use_haiku or self._use_sonnet:
            self._client = ClaudeModerationClient(
                api_key=anthropic_api_key,
                default_model="haiku",
                enable_cache=enable_cache,
            )
        else:
            self._client = None

        self._stats = {
            "total": 0,
            "resolved_at": {level.value: 0 for level in CascadeLevel},
            "total_cost": 0.0,
            "total_input_tokens": 0,
            "total_output_tokens": 0,
            "total_cached_tokens": 0,
        }

    def moderate(self, image_source: str | bytes | Path) -> ModerationResult:
        """Run the full cascade on a single image."""
        self._stats["total"] += 1

        # Level 1: pHash lookup
        if self._use_phash and self._phash_filter and isinstance(image_source, (str, Path)):
            result = self._phash_filter.check(image_source)
            if result is not None:
                self._record(result)
                return result

        # Preprocess for Claude
        b64, meta = preprocess_image(
            image_source,
            max_size=self._max_size,
            quality=self._quality,
        )

        # Level 2: Haiku
        if self._use_haiku:
            result = self._client.moderate(b64, model="haiku")

            needs_escalation = (
                self._use_sonnet
                and not result.safe
                and result.confidence < self._sonnet_threshold
            )
            if not needs_escalation:
                result.details["preprocessing"] = meta
                self._record(result)
                return result

        # Level 3: Sonnet (escalation)
        if self._use_sonnet:
            result = self._client.moderate(b64, model="sonnet")
            result.details["preprocessing"] = meta
            result.details["escalated"] = True
            self._record(result)
            return result

        return ModerationResult(
            safe=True,
            category=ModerationCategory.SAFE,
            confidence=0.0,
            resolved_at=CascadeLevel.HAIKU,
            details={"error": "No cascade level available"},
        )

    def moderate_batch_async(
        self, image_sources: list[str | bytes | Path]
    ) -> str:
        """Submit a batch of images for async moderation via Batch API.

        Returns a batch ID that can be used to retrieve results later.
        """
        images = []
        for src in image_sources:
            b64, _ = preprocess_image(
                src, max_size=self._max_size, quality=self._quality
            )
            images.append((b64, "image/jpeg"))

        return self._client.moderate_batch(images, model="haiku")

    def get_batch_results(self, batch_id: str) -> list[ModerationResult]:
        """Retrieve completed batch results."""
        return self._client.get_batch_results(batch_id)

    @property
    def stats(self) -> dict:
        return {**self._stats}

    def _record(self, result: ModerationResult) -> None:
        self._stats["resolved_at"][result.resolved_at.value] += 1
        self._stats["total_cost"] += result.estimated_cost
        self._stats["total_input_tokens"] += result.input_tokens
        self._stats["total_output_tokens"] += result.output_tokens
        self._stats["total_cached_tokens"] += result.cached_tokens
