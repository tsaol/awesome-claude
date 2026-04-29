"""Batch moderation example — submit many images at 50% cost reduction."""

import time
from pathlib import Path

from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(
    enable_cache=True,
    max_image_size=768,
    cascade_levels=["haiku"],
)

image_dir = Path("images")
image_paths = list(image_dir.glob("*.jpg")) + list(image_dir.glob("*.png"))
print(f"Submitting {len(image_paths)} images for batch moderation...")

batch_id = pipeline.moderate_batch_async(image_paths)
print(f"Batch submitted: {batch_id}")
print("Batch API processes within 24h at 50% cost. Poll for results:")

# In production, poll periodically instead of sleeping
time.sleep(60)
results = pipeline.get_batch_results(batch_id)

flagged = [r for r in results if not r.safe]
print(f"\nResults: {len(results)} processed, {len(flagged)} flagged")
for r in flagged:
    print(f"  - {r.category.value} (confidence: {r.confidence:.2f})")
