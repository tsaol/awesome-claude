"""Pre-filtering layer using perceptual hashing and optional lightweight ML.

This layer handles obvious cases before calling Claude, at zero API cost.
"""

from __future__ import annotations

import io
import warnings
from pathlib import Path

import imagehash
from PIL import Image

from .models import CascadeLevel, ModerationCategory, ModerationResult


class PHashFilter:
    """Compare images against a known-violation hash database."""

    def __init__(self, hash_db_path: str | Path | None = None):
        self._known_hashes: dict[str, ModerationCategory] = {}
        self._parsed: dict[str, imagehash.ImageHash] = {}
        if hash_db_path:
            self._load_db(hash_db_path)

    def _load_db(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return
        for lineno, line in enumerate(path.read_text().splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(",")]
            if len(parts) != 2:
                warnings.warn(f"{path}:{lineno}: expected 'hash,category', skipping")
                continue
            hash_str, category = parts
            try:
                self.add_hash(hash_str, ModerationCategory(category))
            except ValueError as e:
                warnings.warn(f"{path}:{lineno}: skipping invalid row ({e})")

    def add_hash(self, hash_str: str, category: ModerationCategory) -> None:
        """Add a known-violation hash. Raises ValueError on a malformed hash."""
        try:
            parsed = imagehash.hex_to_hash(hash_str)
        except (ValueError, TypeError) as e:
            raise ValueError(f"invalid hash {hash_str!r}: {e}") from e
        if parsed.hash.shape != (8, 8):
            raise ValueError(f"invalid hash {hash_str!r}: expected 16 hex chars (64-bit pHash)")
        self._known_hashes[hash_str] = category
        self._parsed[hash_str] = parsed

    def save_db(self, path: str | Path) -> None:
        lines = [f"{h},{c.value}" for h, c in self._known_hashes.items()]
        Path(path).write_text("\n".join(lines) + "\n")

    def check(
        self, image_path: str | Path | bytes, threshold: int = 8
    ) -> ModerationResult | None:
        """Check if image matches any known violation hash.

        Args:
            image_path: Path to the image file, or raw image bytes.
            threshold: Hamming distance threshold (lower = stricter).

        Returns:
            ModerationResult if match found, None otherwise.
        """
        if not self._known_hashes:
            return None
        img_hash = _phash(image_path)

        for known_hash_str, category in self._known_hashes.items():
            distance = int(img_hash - self._parsed[known_hash_str])
            if distance <= threshold:
                confidence = float(max(0.0, 1.0 - distance / 64.0))
                return ModerationResult(
                    safe=False,
                    category=category,
                    confidence=confidence,
                    resolved_at=CascadeLevel.PHASH,
                    details={
                        "matched_hash": known_hash_str,
                        "distance": distance,
                    },
                )
        return None

    @staticmethod
    def compute_hash(image_path: str | Path | bytes) -> str:
        return str(_phash(image_path))


def _phash(source: str | Path | bytes) -> imagehash.ImageHash:
    fp = io.BytesIO(source) if isinstance(source, bytes) else source
    with Image.open(fp) as img:
        return imagehash.phash(img)
