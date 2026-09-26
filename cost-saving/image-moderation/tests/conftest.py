"""Shared fakes: an Anthropic-compatible client that never touches the network."""

import json
from types import SimpleNamespace

import pytest


def make_message(text=None, *, stop_reason="end_turn", model="claude-haiku-4-5",
                 input_tokens=800, output_tokens=25, cache_read=0, cache_write=0,
                 content=None):
    if content is None:
        content = [] if text is None else [SimpleNamespace(type="text", text=text)]
    return SimpleNamespace(
        id="msg_fake",
        type="message",
        role="assistant",
        model=model,
        content=content,
        stop_reason=stop_reason,
        stop_details=None,
        usage=SimpleNamespace(
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            cache_read_input_tokens=cache_read,
            cache_creation_input_tokens=cache_write,
        ),
    )


def verdict(safe, category, confidence, reason="test"):
    return json.dumps(
        {"safe": safe, "category": category, "confidence": confidence, "reason": reason}
    )


class FakeMessages:
    def __init__(self, responder):
        self._responder = responder
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        out = self._responder(kwargs)
        if isinstance(out, Exception):
            raise out
        return out


class FakeClient:
    """`responder(kwargs) -> message | Exception`, or a dict model_id -> text."""

    def __init__(self, responder):
        if isinstance(responder, dict):
            table = responder
            responder = lambda kw: make_message(table[kw["model"]], model=kw["model"])
        self.messages = FakeMessages(responder)

    @property
    def calls(self):
        return self.messages.calls


@pytest.fixture
def png_bytes():
    import io
    from PIL import Image

    buf = io.BytesIO()
    Image.new("RGB", (1200, 900), (10, 120, 200)).save(buf, "PNG")
    return buf.getvalue()
