import pytest

from image_moderation.models import PRICING, estimate_cost


def test_cost_input_output_only():
    # Haiku 4.5: $1 / $5 per MTok
    assert estimate_cost("haiku", 1_000_000, 1_000_000) == pytest.approx(6.0)


def test_cache_tokens_are_additive_not_subtracted():
    # input_tokens from the API already excludes cache reads/writes.
    cost = estimate_cost("haiku", 100, 0, cache_read_tokens=5000, cache_creation_tokens=0)
    expected = (100 * 1.00 + 5000 * 0.10) / 1_000_000
    assert cost == pytest.approx(expected)
    assert cost > 0


def test_cache_write_rate():
    cost = estimate_cost("sonnet", 0, 0, cache_creation_tokens=1_000_000)
    assert cost == pytest.approx(PRICING["sonnet"]["input"] * 1.25)


def test_never_negative():
    assert estimate_cost("haiku", 0, 0, cache_read_tokens=10_000) >= 0
    assert estimate_cost("haiku", -5, -5, -5, -5) == 0


def test_batch_discount():
    full = estimate_cost("sonnet", 1000, 100, 200, 300)
    assert estimate_cost("sonnet", 1000, 100, 200, 300, batch=True) == pytest.approx(full / 2)


def test_full_model_id_resolves_pricing():
    assert estimate_cost("claude-sonnet-5", 1_000_000, 0) == pytest.approx(2.0)
    with pytest.raises(ValueError):
        estimate_cost("gpt-x", 1, 1)
