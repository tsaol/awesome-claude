from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ModerationCategory(str, Enum):
    SAFE = "safe"
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    HATE = "hate"
    SELF_HARM = "self_harm"
    DRUGS = "drugs"
    WEAPONS = "weapons"
    SPAM = "spam"
    OTHER = "other"

    @classmethod
    def parse(cls, value: object) -> "ModerationCategory":
        """Map a model-supplied category string to an enum; unknown -> OTHER."""
        try:
            return cls(str(value).strip().lower())
        except ValueError:
            return cls.OTHER


class CascadeLevel(str, Enum):
    PHASH = "phash"
    PREFILTER = "prefilter"
    HAIKU = "haiku"
    SONNET = "sonnet"
    # No level could make a decision (e.g. no model level enabled, or every
    # model call failed). Always paired with needs_review=True.
    UNRESOLVED = "unresolved"


@dataclass
class ModerationResult:
    # Fail-closed: when needs_review is True, safe is False so that callers
    # filtering on `not result.safe` still surface the image.
    safe: bool
    category: ModerationCategory
    confidence: float
    resolved_at: CascadeLevel
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0  # cache_read_input_tokens
    cache_creation_tokens: int = 0  # cache_creation_input_tokens
    estimated_cost: float = 0.0
    needs_review: bool = False
    details: dict = field(default_factory=dict)

    @property
    def cost_summary(self) -> str:
        review = " | NEEDS REVIEW" if self.needs_review else ""
        return (
            f"Level: {self.resolved_at.value} | "
            f"Tokens: {self.input_tokens}in/{self.output_tokens}out "
            f"({self.cached_tokens} cache read, "
            f"{self.cache_creation_tokens} cache write) | "
            f"Cost: ${self.estimated_cost:.6f}{review}"
        )


def needs_review_result(
    reason: str,
    resolved_at: CascadeLevel = CascadeLevel.UNRESOLVED,
    **details,
) -> ModerationResult:
    """An explicit 'could not decide' result. Never reports the image as safe."""
    return ModerationResult(
        safe=False,
        category=ModerationCategory.OTHER,
        confidence=0.0,
        resolved_at=resolved_at,
        needs_review=True,
        details={"error": reason, **details},
    )


# USD per million tokens, Claude API first-party list prices.
# haiku  = Claude Haiku 4.5, sonnet = Claude Sonnet 5.
# cache_write is the 5-minute-TTL rate (1.25x input); cache_read is 0.1x input.
PRICING = {
    "haiku": {"input": 1.00, "output": 5.00, "cache_read": 0.10, "cache_write": 1.25},
    "sonnet": {"input": 2.00, "output": 10.00, "cache_read": 0.20, "cache_write": 2.50},
}

# Message Batches API bills every token (incl. cache reads/writes) at 50%.
BATCH_DISCOUNT = 0.5


def _pricing_for(model: str) -> dict:
    """Accept a pricing key ("haiku") or a full model ID ("claude-sonnet-5")."""
    if model in PRICING:
        return PRICING[model]
    for key, prices in PRICING.items():
        if key in model:
            return prices
    raise ValueError(f"No pricing known for model {model!r}")


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
    cache_read_tokens: int = 0,
    cache_creation_tokens: int = 0,
    batch: bool = False,
) -> float:
    """Cost in USD for one request, from the API's `usage` fields.

    The API's `input_tokens` already excludes cache reads and cache writes
    (total prompt = input + cache_read + cache_creation), so the three are
    billed independently and nothing is subtracted.
    """
    prices = _pricing_for(model)
    cost = (
        max(0, input_tokens) * prices["input"]
        + max(0, cache_read_tokens) * prices["cache_read"]
        + max(0, cache_creation_tokens) * prices["cache_write"]
        + max(0, output_tokens) * prices["output"]
    ) / 1_000_000
    if batch:
        cost *= BATCH_DISCOUNT
    return cost
