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


class CascadeLevel(str, Enum):
    PHASH = "phash"
    PREFILTER = "prefilter"
    HAIKU = "haiku"
    SONNET = "sonnet"


@dataclass
class ModerationResult:
    safe: bool
    category: ModerationCategory
    confidence: float
    resolved_at: CascadeLevel
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    estimated_cost: float = 0.0
    details: dict = field(default_factory=dict)

    @property
    def cost_summary(self) -> str:
        return (
            f"Level: {self.resolved_at.value} | "
            f"Tokens: {self.input_tokens}in/{self.output_tokens}out "
            f"({self.cached_tokens} cached) | "
            f"Cost: ${self.estimated_cost:.6f}"
        )


# Pricing per million tokens (as of 2026)
PRICING = {
    "haiku": {"input": 0.80, "output": 4.00, "cache_read": 0.08},
    "sonnet": {"input": 3.00, "output": 15.00, "cache_read": 0.30},
}


def estimate_cost(
    model: str, input_tokens: int, output_tokens: int, cached_tokens: int = 0
) -> float:
    prices = PRICING.get(model, PRICING["haiku"])
    uncached_input = input_tokens - cached_tokens
    cost = (
        uncached_input * prices["input"] / 1_000_000
        + cached_tokens * prices["cache_read"] / 1_000_000
        + output_tokens * prices["output"] / 1_000_000
    )
    return cost
