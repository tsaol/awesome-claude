from types import SimpleNamespace

import anthropic
import httpx
import pytest

from image_moderation.client import ClaudeModerationClient, _parse_response
from image_moderation.models import CascadeLevel, ModerationCategory

from conftest import FakeClient, make_message, verdict


def run(text=None, **msg_kwargs):
    fake = FakeClient(lambda kw: make_message(text, model=kw["model"], **msg_kwargs))
    return ClaudeModerationClient(client=fake).moderate("b64data")


def test_valid_response():
    r = run(verdict(False, "violence", 0.93), cache_read=0, input_tokens=700)
    assert (r.safe, r.category, r.confidence, r.needs_review) == (
        False, ModerationCategory.VIOLENCE, 0.93, False)
    assert r.resolved_at == CascadeLevel.HAIKU
    assert r.estimated_cost == pytest.approx((700 * 1.0 + 25 * 5.0) / 1e6)


def test_code_fenced_json():
    r = run("```json\n" + verdict(True, "safe", 0.99) + "\n```")
    assert r.safe is True and not r.needs_review


def test_unknown_category_maps_to_other():
    r = run(verdict(False, "gore", 0.8))
    assert r.category == ModerationCategory.OTHER and not r.needs_review


@pytest.mark.parametrize("text", ['[{"safe": true}]', "not json at all", '"safe"',
                                  '{"category": "safe"}', '{"safe": "yes"}', "null"])
def test_bad_payloads_need_review(text):
    r = run(text)
    assert r.needs_review and r.safe is False and r.confidence == 0.0
    assert _parse_response(text) is None


def test_confidence_clamped_and_coerced():
    assert _parse_response('{"safe": true, "confidence": 7}')["confidence"] == 1.0
    assert _parse_response('{"safe": true, "confidence": "high"}')["confidence"] == 0.0


def test_refusal():
    r = run(None, stop_reason="refusal")
    assert r.needs_review and not r.safe
    assert "refused" in r.details["error"]


def test_no_text_block():
    content = [SimpleNamespace(type="thinking", thinking="")]
    r = run(None, content=content)
    assert r.needs_review and "No text" in r.details["error"]


def test_api_error_returns_result():
    req = httpx.Request("POST", "https://api.anthropic.com/v1/messages")
    err = anthropic.APIConnectionError(request=req)
    client = ClaudeModerationClient(client=FakeClient(lambda kw: err))
    r = client.moderate("b64", model="sonnet")
    assert r.needs_review and r.resolved_at == CascadeLevel.SONNET
    assert "APIConnectionError" in r.details["error"]


def test_model_ids_and_sonnet_thinking_disabled():
    fake = FakeClient(lambda kw: make_message(verdict(True, "safe", 0.9), model=kw["model"]))
    c = ClaudeModerationClient(client=fake)
    c.moderate("b64", model="haiku")
    c.moderate("b64", model="sonnet")
    assert fake.calls[0]["model"] == "claude-haiku-4-5"
    assert "thinking" not in fake.calls[0]
    assert fake.calls[1]["model"] == "claude-sonnet-5"
    assert fake.calls[1]["thinking"] == {"type": "disabled"}


class FakeBatches:
    def __init__(self, entries):
        self.entries = entries
        self.created = None

    def create(self, requests):
        self.created = requests
        return SimpleNamespace(id="batch_1")

    def retrieve(self, batch_id):
        return SimpleNamespace(processing_status="ended")

    def results(self, batch_id):
        return iter(self.entries)


def test_batch_results_keep_custom_id_and_failures():
    ok = make_message(verdict(False, "spam", 0.9), model="claude-haiku-4-5",
                      input_tokens=1000, output_tokens=20)
    entries = [
        SimpleNamespace(custom_id="img_2", result=SimpleNamespace(type="expired")),
        SimpleNamespace(custom_id="img_0", result=SimpleNamespace(type="succeeded", message=ok)),
        SimpleNamespace(custom_id="img_1", result=SimpleNamespace(
            type="errored", error=SimpleNamespace(type="invalid_request_error"))),
    ]
    fake = SimpleNamespace(messages=SimpleNamespace(batches=FakeBatches(entries)))
    c = ClaudeModerationClient(client=fake)
    assert c.moderate_batch([("a", "image/jpeg"), ("b", "image/jpeg")]) == "batch_1"
    assert [r["custom_id"] for r in fake.messages.batches.created] == ["img_0", "img_1"]
    assert c.get_batch_status("batch_1") == "ended"

    results = c.get_batch_results("batch_1")
    assert [r.details["custom_id"] for r in results] == ["img_0", "img_1", "img_2"]
    assert results[0].category == ModerationCategory.SPAM and not results[0].needs_review
    # batch pricing is 50% off
    assert results[0].estimated_cost == pytest.approx((1000 * 1.0 + 20 * 5.0) / 1e6 / 2)
    assert results[1].needs_review and "errored" in results[1].details["error"]
    assert results[2].needs_review and results[2].details["batch_result_type"] == "expired"
