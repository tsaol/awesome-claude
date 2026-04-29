"""Cost comparison: naive vs. optimized image moderation pipeline."""

from image_moderation.models import estimate_cost

IMAGES_PER_MONTH = 1_000_000

print("=" * 60)
print("Cost Comparison: 1M images/month")
print("=" * 60)

# Scenario 1: Raw images → Sonnet (no optimization)
avg_tokens_raw = 5000
cost_naive = estimate_cost("sonnet", avg_tokens_raw, 200) * IMAGES_PER_MONTH
print(f"\n1. Naive (raw → Sonnet):")
print(f"   Avg tokens/image: {avg_tokens_raw}")
print(f"   Monthly cost: ${cost_naive:,.2f}")

# Scenario 2: Resized images → Haiku
avg_tokens_resized = 1000
cost_resized = estimate_cost("haiku", avg_tokens_resized, 50) * IMAGES_PER_MONTH
print(f"\n2. Resized → Haiku:")
print(f"   Avg tokens/image: {avg_tokens_resized}")
print(f"   Monthly cost: ${cost_resized:,.2f}")
print(f"   Savings: {(1 - cost_resized / cost_naive) * 100:.0f}%")

# Scenario 3: Resized + cached → Haiku
system_tokens = 500
cached_ratio = 0.95
cached_tokens = int(system_tokens * cached_ratio)
cost_cached = (
    estimate_cost("haiku", avg_tokens_resized, 50, cached_tokens) * IMAGES_PER_MONTH
)
print(f"\n3. Resized + cached → Haiku:")
print(f"   Monthly cost: ${cost_cached:,.2f}")
print(f"   Savings: {(1 - cost_cached / cost_naive) * 100:.0f}%")

# Scenario 4: Full pipeline (only 10% reach Claude)
api_rate = 0.10
cost_pipeline = cost_cached * api_rate
print(f"\n4. Full pipeline (pre-filter + cascade, 10% to Claude):")
print(f"   Monthly cost: ${cost_pipeline:,.2f}")
print(f"   Savings: {(1 - cost_pipeline / cost_naive) * 100:.0f}%")

# Scenario 5: Full pipeline + Batch API (additional 50% off)
cost_batch = cost_pipeline * 0.5
print(f"\n5. Full pipeline + Batch API:")
print(f"   Monthly cost: ${cost_batch:,.2f}")
print(f"   Savings: {(1 - cost_batch / cost_naive) * 100:.0f}%")

print(f"\n{'=' * 60}")
print(f"Total potential savings: ${cost_naive - cost_batch:,.2f}/month")
print(f"Cost reduction: {(1 - cost_batch / cost_naive) * 100:.1f}%")
