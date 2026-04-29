# Image Moderation Pipeline

Cost-optimized image content moderation using Claude's vision capabilities.

## Core Strategies

1. **Image preprocessing** — Resize/compress to minimize token usage
2. **Tiered cascade** — pHash → lightweight ML → Haiku → Sonnet
3. **Prompt caching** — Cache moderation rules for 90% token savings
4. **Batch API** — 50% cost reduction for non-realtime workloads
5. **Structured output** — Minimal JSON responses to cut output tokens

## Usage

```bash
pip install -e .
```

```python
from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(
    anthropic_api_key="sk-...",
    enable_cache=True,
    cascade_levels=["prefilter", "haiku", "sonnet"],
)

result = pipeline.moderate("path/to/image.jpg")
print(result)
# ModerationResult(safe=False, category="violence", confidence=0.95, cost=0.0003)
```

## Cost Comparison

| Strategy | Tokens/Image | Monthly Cost (1M images) |
|----------|-------------|------------------------|
| Raw → Sonnet | ~5000 | $$$$$ |
| Resized → Haiku | ~1000 | $$ |
| Full pipeline | ~100 (avg) | $ |
