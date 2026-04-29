# Image Moderation Pipeline

**[中文版](README_CN.md)** | English

Cost-optimized image content moderation using Claude's vision capabilities. Combines preprocessing, perceptual hashing, and a tiered model cascade to reduce costs by up to **95%+** compared to naive approaches.

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
│  Preprocess  │ ← Resize to 768px, JPEG quality 75 (reduce tokens ~85%)
└──────┬───────┘
       │
       ▼
┌──────────────┐
│ Claude Haiku │ ← Fast, cheap — handles ~90% of images
└──────┬───────┘
       │ low confidence
       ▼
┌───────────────┐
│ Claude Sonnet │ ← Only for ambiguous cases (~5-10%)
└───────────────┘
```

## Cost Optimization Strategies

| # | Strategy | Savings | How |
|---|----------|---------|-----|
| 1 | Image resizing | ~85% token reduction | 4K→768px reduces tokens from ~8000 to ~1000 |
| 2 | Prompt caching | ~90% on system prompt | Cache moderation rules across requests |
| 3 | Tiered cascade | ~90% requests saved | Most images resolved by Haiku or pre-filter |
| 4 | Batch API | 50% per-request | Non-realtime workloads at half price |
| 5 | Structured output | ~80% on output tokens | JSON-only response vs. verbose explanation |
| 6 | Pre-filter (pHash) | 100% for known images | Zero API cost for previously seen violations |

**Combined: ~95%+ total cost reduction**

### Detailed Cost Breakdown (1M images/month, baseline: raw 4K → Sonnet)

| # | Strategy | Before | After | Savings | Monthly Cost Impact |
|---|----------|--------|-------|---------|-------------------|
| 1 | **Image resizing** (4K→768px) | ~8,000 input tokens/image | ~1,000 input tokens/image | **85% fewer input tokens** | $18,000 → $2,250 (-$15,750) |
| 2 | **Prompt caching** (system prompt) | 500 tokens @ $3.00/M (Sonnet) | 500 tokens @ $0.30/M (cache hit) | **90% cheaper on system prompt** | $1,500 → $150 (-$1,350) |
| 3 | **Tiered cascade** (Haiku first) | 1M images × Sonnet ($3.00/M input) | 900K × Haiku ($0.80/M) + 100K × Sonnet ($3.00/M) | **~70% cheaper per-request avg** | $3,000 → $1,020 (-$1,980) |
| 4 | **Batch API** (async 50% off) | Standard API pricing | 50% discount on all tokens | **50% off entire bill** | $1,020 → $510 (-$510) |
| 5 | **Structured output** (JSON only) | ~150 output tokens @ $15.00/M (Sonnet) | ~20 output tokens @ $4.00/M (Haiku) | **96% cheaper on output** | $2,250 → $80 (-$2,170) |
| 6 | **pHash pre-filter** (known images) | 100% images hit API | ~90% images hit API (10% filtered free) | **10% fewer API calls** | Removes ~$50-100 at pipeline level |

> **Note:** Rows are not strictly additive — strategies compound. The table shows the isolated impact of each technique. When combined sequentially, total cost drops from **~$18,000 to ~$33/month**.

### Strategy-by-Strategy Cost Waterfall

```
$18,000  ← Baseline: raw 4K images → Sonnet, verbose output
   │
   │  [1] Image resizing (4K → 768px)         -85% input tokens
   ▼
 $2,700
   │
   │  [2] Switch to Haiku + prompt caching     -73% model cost + cached system prompt
   ▼
   $730
   │
   │  [3] Tiered cascade (only 10% → Sonnet)   -90% Sonnet usage
   ▼
   $340
   │
   │  [5] Structured output (150→20 tokens)    -87% output tokens
   ▼
   $130
   │
   │  [6] pHash pre-filter (10% zero-cost)     -10% API calls
   ▼
   $117
   │
   │  [4] Batch API (50% off remaining)        -50% all tokens
   ▼
    $58  ← Final: full pipeline + batch
```

---

### Strategy 1: Image Resizing (~85% token reduction)

**Why it works:** Claude's vision API converts images into tokens based on pixel count. A 4K image (3840×2160) consumes ~8,000 tokens, while the same image resized to 768×768 uses only ~1,000 tokens. For content moderation, low resolution is sufficient — policy violations (violence, nudity, hate symbols) are visually obvious even at reduced quality.

**How it saves money:** Image tokens are billed as input tokens. By reducing from ~8,000 to ~1,000 tokens per image, you cut 85% of the per-image input cost. At scale (1M images/month), this alone saves thousands of dollars.

**Token count by resolution:**

| Resolution | Pixels | Estimated Tokens |
|-----------|--------|-----------------|
| 200×200 | 40K | ~170 |
| 400×400 | 160K | ~680 |
| 768×768 | 590K | ~1,000 |
| 1080×1920 | 2M | ~2,700 |
| 3840×2160 (4K) | 8.3M | ~8,000+ |

**Implementation:** We resize to `max_size=768` and compress to JPEG quality 75. We also strip EXIF metadata and convert RGBA→RGB to avoid unnecessary overhead.

```python
from image_moderation import preprocess_image

b64, meta = preprocess_image("photo_4k.jpg", max_size=768, quality=75)
print(meta)
# {'original_size': (3840, 2160), 'final_size': (768, 432),
#  'bytes_original': 4200000, 'bytes_compressed': 85000,
#  'estimated_tokens': 1000}
```

---

### Strategy 2: Prompt Caching (~90% savings on system prompt tokens)

**Why it works:** Every moderation request sends the same system prompt — the moderation rules, category definitions, and output format instructions. Without caching, you pay full price for these tokens on every single request. Anthropic's prompt caching stores the system prompt server-side and reuses it across requests, charging only 10% of the normal input token rate for cache hits.

**How it saves money:** A typical moderation system prompt is 500-1,000 tokens. With 1M requests/month, that's 500M-1B tokens just for the system prompt. At Haiku's input price ($0.80/M tokens), that's $400-800/month. With caching, cache hits cost $0.08/M tokens — reducing this to $40-80/month.

**Cache hit rate:** In a production moderation pipeline with steady traffic, cache hit rates typically exceed 95%, because the system prompt rarely changes.

```python
# Caching is enabled by default in the pipeline.
# The system prompt gets cache_control: {"type": "ephemeral"}
# which tells Anthropic to cache it for ~5 minutes.
#
# With steady request flow, nearly every request hits the cache.

pipeline = ImageModerationPipeline(enable_cache=True)  # default

# Check cache performance in results:
result = pipeline.moderate("image.jpg")
print(f"Cached tokens: {result.cached_tokens}")  # e.g., 500 out of 1500 input tokens
```

---

### Strategy 3: Tiered Cascade (~90% cost reduction through routing)

**Why it works:** Not all images need the same level of analysis. Most images are obviously safe or obviously unsafe — only a small fraction are genuinely ambiguous. By using cheaper models (or no model at all) for easy cases, and only escalating to expensive models for hard cases, you dramatically reduce average cost per image.

**How it saves money:**

| Cascade Level | Cost per Image | Traffic Share | Purpose |
|--------------|---------------|--------------|---------|
| pHash pre-filter | $0 | ~5-10% | Known violations matched by hash |
| Claude Haiku | ~$0.001 | ~85-90% | Fast, cheap — handles most cases |
| Claude Sonnet | ~$0.005 | ~5-10% | High accuracy for ambiguous content |

If 90% of images are handled by Haiku at $0.001 and only 10% escalate to Sonnet at $0.005, the blended average is $0.0014/image instead of $0.005/image (Sonnet for all) — a 72% savings on Claude API costs alone.

**Escalation logic:** When Haiku returns a result with confidence below the `sonnet_threshold` (default: 0.7), the image automatically escalates to Sonnet for a second opinion. Safe images with high confidence never escalate.

```python
pipeline = ImageModerationPipeline(
    sonnet_threshold=0.7,  # escalate if Haiku confidence < 70%
    cascade_levels=["phash", "haiku", "sonnet"],
)

# After processing, check where images were resolved:
print(pipeline.stats)
# {'total': 10000, 'resolved_at': {'phash': 500, 'haiku': 8600, 'sonnet': 900}, ...}
```

---

### Strategy 4: Batch API (50% cost reduction)

**Why it works:** Anthropic's Message Batches API offers a 50% discount on all token costs in exchange for asynchronous processing. Instead of getting results in real-time, you submit a batch and receive results within 24 hours. For moderation workflows that don't need instant results — such as nightly review of user-uploaded content, backlog audits, or periodic sweeps — this is free money.

**How it saves money:** The 50% discount applies to all tokens (input, output, and cached). This stacks with all other optimizations. If your optimized per-image cost is $0.001, Batch API brings it to $0.0005.

**When to use it:**
- Nightly/weekly content review sweeps
- Backlog moderation of existing content
- Re-moderation after policy updates
- Training data labeling

**When NOT to use it:**
- Real-time upload moderation (users expect instant feedback)
- Live-stream content filtering

```python
from pathlib import Path

images = list(Path("uploads/today/").glob("*.jpg"))
batch_id = pipeline.moderate_batch_async(images)  # returns immediately
print(f"Submitted {len(images)} images, batch ID: {batch_id}")

# Hours later, retrieve results:
results = pipeline.get_batch_results(batch_id)
flagged = [r for r in results if not r.safe]
print(f"Flagged: {len(flagged)}/{len(results)}")
```

---

### Strategy 5: Structured Output (~80% savings on output tokens)

**Why it works:** Output tokens are significantly more expensive than input tokens across all Claude models:

| Model | Input Price | Output Price | Output/Input Ratio |
|-------|-----------|-------------|-------------------|
| Haiku | $0.80/M | $4.00/M | **5x** |
| Sonnet | $3.00/M | $15.00/M | **5x** |

A verbose moderation response ("This image appears to contain graphic violence depicting...") can easily consume 100-200 output tokens. A structured JSON response (`{"safe": false, "category": "violence", "confidence": 0.95}`) uses only ~20 tokens — an 80-90% reduction.

**How it saves money:** For 1M images on Haiku, reducing output from 150 to 20 tokens saves:
- Before: 150M output tokens × $4.00/M = $600/month
- After: 20M output tokens × $4.00/M = $80/month
- **Savings: $520/month** just from output compression

**Implementation:** The system prompt explicitly instructs Claude to respond with JSON only, and `max_tokens` is set to 100 (a safety margin — actual responses are ~20 tokens).

```python
# The client enforces structured output:
# - System prompt: "Respond with ONLY a JSON object, no other text"
# - max_tokens=100 (prevents runaway responses)
# - Response format: {"safe": bool, "category": str, "confidence": float, "reason": str}
```

---

### Strategy 6: Pre-filter with Perceptual Hashing (100% savings for known images)

**Why it works:** Perceptual hashing (pHash) generates a fingerprint of an image's visual content that is robust to resizing, compression, and minor edits. By maintaining a database of hashes from previously identified violations, you can instantly match re-uploads and near-duplicates without ever calling the Claude API.

**How it saves money:** Every image matched by pHash costs exactly $0 in API calls. In platforms where users re-upload the same violating content (common in spam/abuse scenarios), this can filter out 5-20% of all images for free.

**How it handles variants:** Unlike exact file hashes (MD5/SHA), pHash compares visual similarity. Two images that are:
- Different file formats (JPEG vs PNG) → same pHash
- Different resolutions → same pHash
- Slightly cropped or color-adjusted → similar pHash (within threshold)

The `threshold` parameter (default: 8) controls strictness. Lower = stricter matching, fewer false positives. Higher = more lenient, catches more variants but risks false positives.

```python
from image_moderation.prefilter import PHashFilter
from image_moderation.models import ModerationCategory

# Build a hash database from confirmed violations
phash = PHashFilter()
phash.add_hash(phash.compute_hash("known_spam_1.jpg"), ModerationCategory.SPAM)
phash.add_hash(phash.compute_hash("known_violence_1.jpg"), ModerationCategory.VIOLENCE)
phash.save_db("known_violations.csv")

# In production, matches are instant and free:
result = phash.check("user_upload.jpg", threshold=8)
if result:
    print(f"Matched known violation: {result.category} (confidence: {result.confidence})")
```

## Quick Start

```bash
cd skills/image-moderation
pip install -e .
```

### Single Image

```python
from image_moderation import ImageModerationPipeline

pipeline = ImageModerationPipeline(
    enable_cache=True,
    max_image_size=768,
    sonnet_threshold=0.7,
)

result = pipeline.moderate("photo.jpg")
print(result.safe)          # True/False
print(result.category)      # ModerationCategory.SAFE
print(result.cost_summary)  # Level: haiku | Tokens: 1050in/25out (500 cached) | Cost: $0.000640
```

### Batch Processing (50% cheaper)

```python
from pathlib import Path

images = list(Path("uploads/").glob("*.jpg"))
batch_id = pipeline.moderate_batch_async(images)

# Poll later (Batch API returns within 24h)
results = pipeline.get_batch_results(batch_id)
flagged = [r for r in results if not r.safe]
```

### With pHash Pre-filter

```python
pipeline = ImageModerationPipeline(
    hash_db_path="known_violations.csv",  # hash,category per line
    cascade_levels=["phash", "haiku", "sonnet"],
)

# Build the hash database over time
from image_moderation.prefilter import PHashFilter
phash = PHashFilter()
h = phash.compute_hash("confirmed_violation.jpg")
phash.add_hash(h, ModerationCategory.VIOLENCE)
phash.save_db("known_violations.csv")
```

## Configuration

| Parameter | Default | Description |
|-----------|---------|-------------|
| `max_image_size` | 768 | Max dimension for resize (lower = cheaper) |
| `image_quality` | 75 | JPEG compression quality |
| `sonnet_threshold` | 0.7 | Confidence below this triggers Sonnet escalation |
| `enable_cache` | True | Cache system prompt for 90% token savings |
| `cascade_levels` | all | Which levels to enable: `phash`, `haiku`, `sonnet` |

## Cost Estimation

Run the cost comparison script:

```bash
python examples/cost_comparison.py
```

Example output for **1M images/month**:

| Strategy | Monthly Cost |
|----------|-------------|
| Naive (raw → Sonnet) | ~$18,000 |
| Resized → Haiku | ~$1,000 |
| Full pipeline + Batch | ~$50 |

## Project Structure

```
image_moderation/
├── __init__.py          # Public API
├── models.py            # Data models, enums, cost estimation
├── preprocessing.py     # Image resize/compress/encode
├── prefilter.py         # pHash matching against known violations
├── client.py            # Claude API wrapper (cache + batch)
└── pipeline.py          # Tiered cascade orchestrator
examples/
├── basic_moderation.py  # Single image example
├── batch_moderation.py  # Batch API example
└── cost_comparison.py   # Cost savings calculator
```
