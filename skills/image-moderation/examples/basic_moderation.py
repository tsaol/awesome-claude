"""Basic image moderation example — single image through the full cascade."""

from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(
    enable_cache=True,
    max_image_size=768,
    image_quality=75,
    sonnet_threshold=0.7,
    cascade_levels=["haiku", "sonnet"],
)

result = pipeline.moderate("test_image.jpg")

print(f"Safe: {result.safe}")
print(f"Category: {result.category.value}")
print(f"Confidence: {result.confidence:.2f}")
print(f"Cost: {result.cost_summary}")
