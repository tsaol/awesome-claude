"""Batch moderation example — submit many images at 50% cost reduction."""

import time
from pathlib import Path

from image_moderation import ImageModerationPipeline

POLL_INTERVAL_S = 60

pipeline = ImageModerationPipeline(
    enable_cache=True,
    max_image_size=768,
    cascade_levels=["haiku"],
)

image_dir = Path("images")
image_paths = sorted(image_dir.glob("*.jpg")) + sorted(image_dir.glob("*.png"))
print(f"Submitting {len(image_paths)} images for batch moderation...")

batch_id = pipeline.moderate_batch_async(image_paths)
print(f"Batch submitted: {batch_id}")
print("Batch API processes within 24h at 50% cost. Polling for completion...")

while (status := pipeline.get_batch_status(batch_id)) != "ended":
    print(f"  status: {status}; checking again in {POLL_INTERVAL_S}s")
    time.sleep(POLL_INTERVAL_S)

results = pipeline.get_batch_results(batch_id)

# custom_id "img_<i>" maps back to image_paths[i]
flagged = [r for r in results if not r.safe]
print(f"\nResults: {len(results)} processed, {len(flagged)} flagged")
for r in flagged:
    idx = int(r.details["custom_id"].rsplit("_", 1)[1])
    label = "NEEDS REVIEW" if r.needs_review else r.category.value
    print(f"  - {image_paths[idx]}: {label} (confidence: {r.confidence:.2f})")
