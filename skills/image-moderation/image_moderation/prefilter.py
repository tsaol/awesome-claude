"""Pre-filtering layer using perceptual hashing and optional lightweight ML.

This layer handles obvious cases before calling Claude, at zero API cost.
"""

from pathlib import Path

import imagehash
from PIL import Image

from .models import CascadeLevel, ModerationCategory, ModerationResult


class PHashFilter:
    """Compare images against a known-violation hash database."""

    def __init__(self, hash_db_path: str | Path | None = None):
        self._known_hashes: dict[str, ModerationCategory] = {}
        if hash_db_path:
            self._load_db(hash_db_path)

    def _load_db(self, path: str | Path) -> None:
        path = Path(path)
        if not path.exists():
            return
        for line in path.read_text().strip().splitlines():
            parts = line.strip().split(",", 1)
            if len(parts) == 2:
                hash_str, category = parts
                self._known_hashes[hash_str] = ModerationCategory(category)

    def add_hash(self, hash_str: str, category: ModerationCategory) -> None:
        self._known_hashes[hash_str] = category

    def save_db(self, path: str | Path) -> None:
        lines = [f"{h},{c.value}" for h, c in self._known_hashes.items()]
        Path(path).write_text("\n".join(lines) + "\n")

    def check(self, image_path: str | Path, threshold: int = 8) -> ModerationResult | None:
        """Check if image matches any known violation hash.

        Args:
            image_path: Path to the image file.
            threshold: Hamming distance threshold (lower = stricter).

        Returns:
            ModerationResult if match found, None otherwise.
        """
        img = Image.open(image_path)
        img_hash = imagehash.phash(img)

        for known_hash_str, category in self._known_hashes.items():
            known_hash = imagehash.hex_to_hash(known_hash_str)
            distance = img_hash - known_hash
            if distance <= threshold:
                confidence = max(0.0, 1.0 - distance / 64.0)
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
    def compute_hash(image_path: str | Path) -> str:
        img = Image.open(image_path)
        return str(imagehash.phash(img))
