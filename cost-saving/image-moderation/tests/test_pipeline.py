import pytest

from image_moderation import ImageModerationPipeline
from image_moderation.models import CascadeLevel, ModerationCategory
from image_moderation.prefilter import PHashFilter

from conftest import FakeClient, verdict

HAIKU, SONNET = "claude-haiku-4-5", "claude-sonnet-5"


def pipeline_with(table, **kw):
    fake = FakeClient(table)
    return ImageModerationPipeline(client=fake, **kw), fake


def test_phash_only_does_not_fail_open(png_bytes):
    p = ImageModerationPipeline(cascade_levels=["phash"])
    r = p.moderate(png_bytes)
    assert r.safe is False and r.needs_review
    assert r.resolved_at == CascadeLevel.UNRESOLVED
    s = p.stats
    assert s["total"] == 1 and s["needs_review"] == 1
    assert s["resolved_at"]["unresolved"] == 1


def test_batch_without_model_level_raises(png_bytes):
    p = ImageModerationPipeline(cascade_levels=["phash"])
    with pytest.raises(ValueError, match="haiku"):
        p.moderate_batch_async([png_bytes])


def test_prefilter_alias_and_unknown_level():
    p = ImageModerationPipeline(cascade_levels=["prefilter"])
    assert p._use_phash
    with pytest.raises(ValueError, match="Unknown cascade level"):
        ImageModerationPipeline(cascade_levels=["phash", "gpt"])
    with pytest.raises(ValueError):
        ImageModerationPipeline(cascade_levels=[])


def test_phash_match_short_circuits(tmp_path, png_bytes):
    h = PHashFilter.compute_hash(png_bytes)
    db = tmp_path / "db.csv"
    db.write_text(f"{h},hate\n")
    p, fake = pipeline_with({}, hash_db_path=db)
    r = p.moderate(png_bytes)
    assert r.resolved_at == CascadeLevel.PHASH and r.category == ModerationCategory.HATE
    assert fake.calls == []


def test_confident_haiku_not_escalated(png_bytes):
    p, fake = pipeline_with({HAIKU: verdict(True, "safe", 0.95)})
    r = p.moderate(png_bytes)
    assert r.resolved_at == CascadeLevel.HAIKU and len(fake.calls) == 1
    assert r.details["preprocessing"]["final_size"] == (768, 576)


@pytest.mark.parametrize("safe", [True, False])
def test_low_confidence_escalates_regardless_of_verdict(png_bytes, safe):
    p, fake = pipeline_with({
        HAIKU: verdict(safe, "safe" if safe else "violence", 0.4),
        SONNET: verdict(False, "violence", 0.9),
    })
    r = p.moderate(png_bytes)
    assert [c["model"] for c in fake.calls] == [HAIKU, SONNET]
    assert r.resolved_at == CascadeLevel.SONNET and r.details["escalated"]
    assert r.details["haiku_result"]["confidence"] == 0.4
    s = p.stats
    assert s["escalated"] == 1 and s["resolved_at"]["sonnet"] == 1
    assert s["resolved_at"]["haiku"] == 0
    # both calls billed
    haiku_cost = r.details["haiku_result"]["estimated_cost"]
    assert haiku_cost > 0
    assert s["total_cost"] == pytest.approx(haiku_cost + r.estimated_cost)
    assert s["total_input_tokens"] == 1600


def test_unparseable_haiku_escalates(png_bytes):
    p, fake = pipeline_with({HAIKU: "garbage", SONNET: verdict(True, "safe", 0.9)})
    r = p.moderate(png_bytes)
    assert r.resolved_at == CascadeLevel.SONNET and not r.needs_review


def test_haiku_only_low_confidence_returned_as_is(png_bytes):
    p, fake = pipeline_with({HAIKU: verdict(True, "safe", 0.3)}, cascade_levels=["haiku"])
    r = p.moderate(png_bytes)
    assert r.resolved_at == CascadeLevel.HAIKU and len(fake.calls) == 1


def test_sonnet_only(png_bytes):
    p, fake = pipeline_with({SONNET: verdict(True, "safe", 0.9)}, cascade_levels=["sonnet"])
    r = p.moderate(png_bytes)
    assert r.resolved_at == CascadeLevel.SONNET and "escalated" not in r.details


def test_stats_snapshot_is_a_copy(png_bytes):
    p, _ = pipeline_with({HAIKU: verdict(True, "safe", 0.95)})
    snap = p.stats
    p.moderate(png_bytes)
    assert snap["resolved_at"]["haiku"] == 0
