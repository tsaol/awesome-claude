# Image Moderation Pipeline

Cost-optimized image content moderation using Claude's vision capabilities.

## Core Strategies

1. **Image preprocessing** — EXIF-rotate, flatten alpha, resize/compress to minimize image tokens (~width×height/750)
2. **Tiered cascade** — pHash → Haiku 4.5 → Sonnet 5 (low-confidence results escalate; undetermined results return `needs_review=True`, never "safe")
3. **Batch API** — 50% cost reduction for non-realtime workloads
4. **Structured output** — Minimal JSON responses to cut output tokens
5. **Prompt caching** — `cache_control` is set, but the built-in ~300-token prompt is below the minimum cacheable size (4096 tokens on Haiku 4.5, 1024 on Sonnet 5), so it only helps with a much longer prompt

## Usage

```bash
pip install -e '.[dev]'   # Python 3.9+
```

```python
from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(
    anthropic_api_key="sk-...",
    cascade_levels=["phash", "haiku", "sonnet"],  # "prefilter" is an alias of "phash"
)

result = pipeline.moderate("path/to/image.jpg")
print(result.safe, result.category, result.needs_review, result.cost_summary)
```

## Cost Comparison

From `examples/cost_comparison.py` (1M images/month; traffic numbers are hypothetical inputs — edit them):

| Strategy | Input tokens/image | Monthly Cost |
|----------|-------------|------------------------|
| Raw 4K → Sonnet 5 | ~5,100 | ~$11,700 |
| Resized 768px → Haiku 4.5 | ~760 | ~$913 |
| Full realtime pipeline (10% escalated, 5% pHash hits) | | ~$1,041 (-91%) |
| Batch, Haiku only | | ~$434 (-96%) |
