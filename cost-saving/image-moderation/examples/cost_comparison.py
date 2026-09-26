"""Cost comparison: naive vs. optimized image moderation pipeline.

All traffic-shape numbers below are HYPOTHETICAL inputs, not measurements.
Replace them with your own numbers (e.g. from `pipeline.stats`) before
drawing conclusions. Prices come from image_moderation.models.PRICING and
image token counts from the documented formula (width * height / 750, after
the API's own downscale), via image_moderation.preprocessing.
"""

from image_moderation.client import MODERATION_SYSTEM_PROMPT
from image_moderation.models import BATCH_DISCOUNT, estimate_cost
from image_moderation.preprocessing import estimate_image_tokens

# ---- Hypothetical inputs (edit these) --------------------------------------
IMAGES_PER_MONTH = 1_000_000
RAW_SIZE = (3840, 2160)          # typical upload: 4K, 16:9
RESIZED_SIZE = (768, 432)        # after preprocess_image(max_size=768)
PROMPT_TOKENS = 320              # system prompt + "Classify this image." (approx.)
VERBOSE_OUTPUT_TOKENS = 150      # free-form explanation
JSON_OUTPUT_TOKENS = 30          # {"safe":..,"category":..,"confidence":..,"reason":..}
ESCALATION_RATE = 0.10           # share of Haiku results below sonnet_threshold
PHASH_HIT_RATE = 0.05            # share of uploads matching known-violation hashes
# ----------------------------------------------------------------------------

raw_img_sonnet = estimate_image_tokens(*RAW_SIZE, tier="high_res")
resized_img = estimate_image_tokens(*RESIZED_SIZE)
in_raw = raw_img_sonnet + PROMPT_TOKENS
in_resized = resized_img + PROMPT_TOKENS


def monthly(per_image: float) -> float:
    return per_image * IMAGES_PER_MONTH


def show(n: int, title: str, per_image: float, baseline: float, note: str = "") -> None:
    print(f"\n{n}. {title}")
    if note:
        print(f"   {note}")
    print(f"   Per image:    ${per_image:.6f}")
    print(f"   Monthly cost: ${monthly(per_image):,.2f}")
    if baseline:
        print(f"   vs. naive:    -{(1 - per_image / baseline) * 100:.1f}%")


print("=" * 64)
print(f"Cost Comparison: {IMAGES_PER_MONTH:,} images/month (hypothetical inputs)")
print("=" * 64)
print(f"Image tokens: raw {RAW_SIZE[0]}x{RAW_SIZE[1]} on Sonnet 5 = {raw_img_sonnet} "
      f"(API downscales to its 2576px limit); resized "
      f"{RESIZED_SIZE[0]}x{RESIZED_SIZE[1]} = {resized_img}")

# 1. Raw images -> Sonnet, verbose output
naive = estimate_cost("sonnet", in_raw, VERBOSE_OUTPUT_TOKENS)
show(1, "Naive (raw 4K -> Sonnet 5, verbose output)", naive, 0,
     f"{in_raw} input + {VERBOSE_OUTPUT_TOKENS} output tokens")

# 2. Resized images -> Sonnet
resized_sonnet = estimate_cost("sonnet", in_resized, VERBOSE_OUTPUT_TOKENS)
show(2, "Resized to 768px -> Sonnet 5", resized_sonnet, naive,
     f"{in_resized} input tokens")

# 3. Resized -> Haiku, JSON-only output
haiku = estimate_cost("haiku", in_resized, JSON_OUTPUT_TOKENS)
show(3, "Resized -> Haiku 4.5, JSON-only output", haiku, naive,
     f"{in_resized} input + {JSON_OUTPUT_TOKENS} output tokens")

# 4. Prompt caching: only applies if the cached prefix meets the minimum
print("\n4. Prompt caching")
print(f"   System prompt is ~{len(MODERATION_SYSTEM_PROMPT) // 4} tokens (chars/4); minimum "
      "cacheable prefix is 4096 (Haiku 4.5) / 1024 (Sonnet 5).")
print("   -> nothing is cached; savings $0. (Caching would only matter with a much")
print("      longer policy prompt, and then only on the prompt, not the image.)")

# 5. Cascade: every non-pHash image hits Haiku, ESCALATION_RATE also hits Sonnet
sonnet_json = estimate_cost("sonnet", in_resized, JSON_OUTPUT_TOKENS)
cascade = haiku + ESCALATION_RATE * sonnet_json
show(5, "Cascade: Haiku, escalate low-confidence to Sonnet", cascade, naive,
     f"{ESCALATION_RATE:.0%} escalated (Haiku cost still paid for those)")

# 6. pHash pre-filter skips the API for known violations
pipeline = (1 - PHASH_HIT_RATE) * cascade
show(6, "+ pHash pre-filter", pipeline, naive,
     f"{PHASH_HIT_RATE:.0%} of uploads matched for free")

# 7. Batch API: 50% off all tokens (non-realtime only; no escalation in batch mode)
batch = (1 - PHASH_HIT_RATE) * haiku * BATCH_DISCOUNT
show(7, "Batch API, Haiku only (non-realtime)", batch, naive,
     "50% off; batch mode runs a single model, no escalation")

print(f"\n{'=' * 64}")
print(f"Realtime pipeline (6): ${monthly(pipeline):,.2f}/month, "
      f"-{(1 - pipeline / naive) * 100:.1f}% vs naive ${monthly(naive):,.2f}")
print(f"Batch (7):             ${monthly(batch):,.2f}/month, "
      f"-{(1 - batch / naive) * 100:.1f}% vs naive")
