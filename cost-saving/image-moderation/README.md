# Image Moderation Pipeline

**[中文版](README_CN.md)** | English

Cost-optimized image content moderation using Claude's vision capabilities. Combines preprocessing, perceptual hashing, and a tiered model cascade. With the example assumptions in [`examples/cost_comparison.py`](examples/cost_comparison.py), the realtime pipeline costs **~91% less** than sending raw 4K images to Sonnet, and **~96% less** in batch mode. Your numbers depend on your traffic — rerun the script with your own inputs.

## Architecture

```
User Upload
    │
    ▼
┌──────────────┐
│  pHash Check │ ← Known-violation hash database (zero API cost)
└──────┬───────┘
       │ no match
       ▼
┌──────────────┐
│  Preprocess  │ ← EXIF-rotate, flatten alpha, resize to 768px, JPEG q75
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Claude Haiku │ ← Haiku 4.5: fast, cheap first pass
└──────┬───────┘
       │ confidence < threshold (any verdict), or unparseable/refused/error
       ▼
┌───────────────┐
│ Claude Sonnet │ ← Sonnet 5: second opinion on uncertain cases
└───────────────┘
       │ still undetermined
       ▼
  needs_review=True, safe=False  (never fails open)
```

## Cost Optimization Strategies

| # | Strategy | Savings | How |
|---|----------|---------|-----|
| 1 | Image resizing | 72–91% fewer image tokens | 4K→768×432 = ~443 tokens vs. 1,568 (Haiku) / 4,784 (Sonnet 5) |
| 2 | Tiered cascade | Most requests stay on the cheaper model | Haiku first; escalate only low-confidence results |
| 3 | Batch API | 50% on all tokens | Non-realtime workloads at half price |
| 4 | Structured output | ~80% on output tokens | JSON-only response (~30 tokens) vs. verbose explanation |
| 5 | Pre-filter (pHash) | 100% for known images | Zero API cost for previously seen violations |
| 6 | Prompt caching | **None with the built-in prompt** | Prompt is below the model's minimum cacheable size — see below |

### Cost Breakdown (1M images/month, from `examples/cost_comparison.py`)

Prices: Haiku 4.5 $1 / $5, Sonnet 5 $2 / $10 per million input / output tokens. The traffic numbers (4K 16:9 uploads, ~320 prompt tokens, 150 verbose vs. 30 JSON output tokens, 10% escalation, 5% pHash hit rate) are **hypothetical inputs**, not measurements.

| # | Step | Tokens / image | Monthly cost | vs. naive |
|---|------|---------------|-------------|-----------|
| 1 | Naive: raw 4K → Sonnet 5, verbose output | 5,104 in / 150 out | $11,708 | — |
| 2 | Resize to 768px → Sonnet 5 | 763 in / 150 out | $3,026 | -74.2% |
| 3 | Resize → Haiku 4.5, JSON-only output | 763 in / 30 out | $913 | -92.2% |
| 4 | Prompt caching | — | $0 saved | — |
| 5 | Cascade: Haiku + 10% escalated to Sonnet | | $1,096 | -90.6% |
| 6 | + pHash pre-filter (5% free) | | **$1,041** | **-91.1%** |
| 7 | Batch API, Haiku only (non-realtime) | | **$434** | **-96.3%** |

Step 5 costs more than step 3 because escalation pays for a second opinion on uncertain images — that's an accuracy spend, not a saving. Batch mode runs a single model with no escalation.

---

### Strategy 1: Image Resizing

**Why it works:** Claude bills images as input tokens, roughly `width × height / 750`. Images larger than the model's limit are first downscaled by the API itself: to 1,568 px on the long edge for Haiku 4.5 (capping an image at ~1,568 tokens) and to 2,576 px for Sonnet 5 (up to ~4,784 tokens). So a raw 4K upload is not "8,000 tokens" — it costs ~1,568 on Haiku and ~4,784 on Sonnet 5. Resizing to 768 px yourself brings it down to a few hundred tokens and shrinks the upload. For moderation, 768 px is usually enough to spot policy violations, but validate on your own data.

**Token count by resolution** (`estimate_image_tokens`):

| Resolution | Haiku 4.5 | Sonnet 5 |
|-----------|-----------|----------|
| 200×200 | ~54 | ~54 |
| 400×400 | ~214 | ~214 |
| 768×432 | ~443 | ~443 |
| 768×768 | ~787 | ~787 |
| 1080×1920 | ~1,568 (downscaled) | ~2,765 (downscaled) |
| 3840×2160 (4K) | ~1,568 (downscaled) | ~4,784 (downscaled) |

**Implementation:** `preprocess_image` applies EXIF orientation, flattens transparent images (RGBA/LA/P) onto white, resizes to `max_size=768`, and re-encodes as JPEG quality 75 (which also strips EXIF metadata).

```python
from image_moderation import preprocess_image

b64, meta = preprocess_image("photo_4k.jpg", max_size=768, quality=75)
print(meta)
# {'original_size': (3840, 2160), 'final_size': (768, 432), ...,
#  'estimated_tokens': 443, 'estimated_tokens_original': 1568}
```

---

### Strategy 2: Tiered Cascade

**Why it works:** Most images are easy. A cheaper model handles them; only uncertain ones go to the more capable model.

| Cascade Level | Cost per Image (example) | Purpose |
|--------------|---------------|---------|
| pHash pre-filter | $0 | Known violations matched by hash |
| Claude Haiku 4.5 | ~$0.0009 | First pass on everything else |
| Claude Sonnet 5 | ~$0.0018 (plus the Haiku call already paid) | Second opinion on uncertain cases |

**Escalation logic:** If Haiku's confidence is below `sonnet_threshold` (default 0.7) — whether it said safe or unsafe — or its reply couldn't be used (unparseable, refusal, API error), the image goes to Sonnet. If no level can decide, the result is `needs_review=True` with `safe=False`, and is counted in `stats["needs_review"]`. The pipeline never reports an unchecked image as safe.

```python
pipeline = ImageModerationPipeline(
    sonnet_threshold=0.7,
    cascade_levels=["phash", "haiku", "sonnet"],
)

print(pipeline.stats)
# {'total': 10000, 'resolved_at': {'phash': 500, 'haiku': 8600, 'sonnet': 900, ...},
#  'escalated': 900, 'needs_review': 12, 'total_cost': ..., ...}
```

`total_cost` includes the Haiku calls for escalated images.

---

### Strategy 3: Batch API (50% cost reduction)

**Why it works:** The Message Batches API bills all tokens (input, output, cache reads/writes) at 50% in exchange for asynchronous processing (results within 24 hours). Good for nightly sweeps, backlog audits, and re-moderation after policy changes; not for realtime upload checks.

Batch mode uses one model (Haiku if enabled, else Sonnet) with no escalation. Every submitted image gets a result: failed or expired requests come back as `needs_review` results. Each result carries `details["custom_id"]` (`img_<index>` in submission order).

```python
import time
from pathlib import Path

images = sorted(Path("uploads/today/").glob("*.jpg"))
batch_id = pipeline.moderate_batch_async(images)

while pipeline.get_batch_status(batch_id) != "ended":
    time.sleep(60)

results = pipeline.get_batch_results(batch_id)
flagged = [r for r in results if not r.safe]   # includes needs_review
```

---

### Strategy 4: Structured Output (~80% savings on output tokens)

Output tokens cost 5× input tokens on both models (Haiku 4.5: $1 / $5, Sonnet 5: $2 / $10 per MTok). A verbose explanation easily takes 100–200 output tokens; the JSON verdict takes ~30. The system prompt asks for JSON only and `max_tokens=100` caps runaway replies. On Sonnet 5, thinking is explicitly disabled for this short classification.

Replies are parsed defensively: code fences are stripped, unknown categories map to `other`, confidence is clamped to [0, 1], and anything that isn't a JSON object with a boolean `safe` becomes a `needs_review` result.

---

### Strategy 5: Pre-filter with Perceptual Hashing (100% savings for known images)

Perceptual hashing (pHash) fingerprints visual content and is robust to resizing, re-encoding, and small edits. Re-uploads of known violations match for free.

The `threshold` parameter (default: 8, Hamming distance out of 64 bits) controls strictness. Malformed rows in the hash CSV are skipped with a warning.

```python
from image_moderation.prefilter import PHashFilter
from image_moderation.models import ModerationCategory

phash = PHashFilter()
phash.add_hash(phash.compute_hash("known_spam_1.jpg"), ModerationCategory.SPAM)
phash.save_db("known_violations.csv")   # hash,category per line

result = phash.check("user_upload.jpg", threshold=8)
if result:
    print(f"Matched known violation: {result.category} (confidence: {result.confidence})")
```

---

### Strategy 6: Prompt Caching (does not apply to the built-in prompt)

The client marks the system prompt with `cache_control`, but the API only caches a prefix that meets the model's minimum: **4,096 tokens on Haiku 4.5** and **1,024 tokens on Sonnet 5**. The built-in prompt is ~300 tokens, so nothing is cached and `cached_tokens` stays 0. The marker is harmless. The image itself is unique per request and can never be cached.

If you replace the prompt with a long policy document above the minimum, cache reads are billed at 0.1× input price and cache writes at 1.25×. Check `result.cached_tokens` (`cache_read_input_tokens`) to confirm hits.

## Quick Start

Requires Python 3.9+.

```bash
cd cost-saving/image-moderation
pip install -e '.[dev]'
pytest -q        # unit tests, no API calls
```

### Single Image

```python
from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(max_image_size=768, sonnet_threshold=0.7)

result = pipeline.moderate("photo.jpg")
print(result.safe, result.needs_review)   # True/False, True if a human should look
print(result.category)                    # ModerationCategory.SAFE
print(result.cost_summary)
# Level: haiku | Tokens: 770in/28out (0 cache read, 0 cache write) | Cost: $0.000910
```

### With pHash Pre-filter

```python
pipeline = ImageModerationPipeline(
    hash_db_path="known_violations.csv",
    cascade_levels=["phash", "haiku", "sonnet"],   # "prefilter" is accepted as an alias of "phash"
)
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_image_size` | 768 | Max dimension for resize (lower = cheaper) |
| `image_quality` | 75 | JPEG compression quality |
| `sonnet_threshold` | 0.7 | Haiku confidence below this (any verdict) triggers Sonnet |
| `enable_cache` | True | Add `cache_control` to the system prompt (only effective above the model's minimum prompt size) |
| `cascade_levels` | all | Any of `phash` (alias `prefilter`), `haiku`, `sonnet`; unknown names raise `ValueError` |
| `client` | None | Pre-built `anthropic.Anthropic`-compatible client (useful for tests) |

## Cost Estimation

```bash
python examples/cost_comparison.py
```

Edit the hypothetical inputs at the top of the script (image size, escalation rate, pHash hit rate, output length) to match your traffic. With the defaults:

| Strategy | Monthly Cost (1M images) |
|----------|-------------|
| Naive (raw 4K → Sonnet 5) | ~$11,700 |
| Resized → Haiku 4.5 | ~$913 |
| Full realtime pipeline | ~$1,041 |
| Batch, Haiku only | ~$434 |

## Project Structure

```
image_moderation/
├── __init__.py          # Public API
├── models.py            # Data models, enums, pricing, cost estimation
├── preprocessing.py     # Image orient/flatten/resize/encode + token estimate
├── prefilter.py         # pHash matching against known violations
├── client.py            # Claude API wrapper (parsing, errors, batch)
└── pipeline.py          # Tiered cascade orchestrator
examples/
├── basic_moderation.py  # Single image example
├── batch_moderation.py  # Batch API example (polls until ended)
└── cost_comparison.py   # Cost calculator (hypothetical inputs)
tests/                   # pytest suite with a fake Anthropic client
```
