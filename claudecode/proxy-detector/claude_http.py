"""Minimal Anthropic Messages API client shared by detect.py and monitor.py.

Raw httpx (not the SDK) on purpose: the detector needs the real HTTP status,
response headers, and per-event stream timing of whatever endpoint it is
pointed at, including non-conforming proxies.

Every call returns a dict with ``ok`` set only when the HTTP status is 2xx and
the body/stream contains no error. Callers must treat ``ok == False`` as an
inconclusive (ERROR) measurement, never as evidence of a model swap.
"""

import json
import re
import time
from typing import Optional

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    raise SystemExit(1)


def _text_from_content(content) -> str:
    """Join all text blocks (responses may start with thinking blocks)."""
    if not isinstance(content, list):
        return ""
    return "".join(b.get("text", "") for b in content
                   if isinstance(b, dict) and b.get("type") == "text")


def call_api(base_url: str, api_key: str, prompt: str, model: str,
             max_tokens: int = 1024, system: Optional[str] = None,
             stream: bool = False, timeout: float = 120) -> dict:
    headers = {
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    body = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": prompt}],
    }
    if system:
        body["system"] = system
    if stream:
        body["stream"] = True

    url = f"{base_url.rstrip('/')}/messages"
    result = {
        "ok": False, "status": 0, "elapsed": 0.0, "ttft": None,
        "gen_time": None, "tps": None, "text": "", "model": None,
        "stop_reason": None, "input_tokens": None, "output_tokens": None,
        "headers": {}, "error": None,
    }
    start = time.monotonic()
    try:
        with httpx.Client(timeout=timeout) as client:
            if stream:
                _do_stream(client, url, headers, body, start, result)
            else:
                _do_plain(client, url, headers, body, result)
    except Exception as e:  # network errors, timeouts, bad JSON
        result["error"] = f"{type(e).__name__}: {e}"
        result["ok"] = False
    result["elapsed"] = time.monotonic() - start
    return result


def _fail(result: dict, msg: str) -> None:
    result["ok"] = False
    result["error"] = msg[:500]


def _do_plain(client, url, headers, body, result):
    resp = client.post(url, headers=headers, json=body)
    result["status"] = resp.status_code
    result["headers"] = dict(resp.headers)
    if not 200 <= resp.status_code < 300:
        return _fail(result, f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if not isinstance(data, dict) or data.get("type") == "error" or "error" in data:
        return _fail(result, f"error body: {json.dumps(data)[:400]}")
    if data.get("type") != "message" and "content" not in data:
        return _fail(result, f"not a Messages API response: {json.dumps(data)[:400]}")
    usage = data.get("usage") or {}
    result.update(
        ok=True,
        text=_text_from_content(data.get("content")),
        model=data.get("model"),
        stop_reason=data.get("stop_reason"),
        input_tokens=usage.get("input_tokens"),
        output_tokens=usage.get("output_tokens"),
    )


def _do_stream(client, url, headers, body, start, result):
    first_event = None
    last_event = None
    got_stop = False
    with client.stream("POST", url, headers=headers, json=body) as resp:
        result["status"] = resp.status_code
        result["headers"] = dict(resp.headers)
        if not 200 <= resp.status_code < 300:
            resp.read()
            return _fail(result, f"HTTP {resp.status_code}: {resp.text}")
        parts = []
        for line in resp.iter_lines():
            if not line.startswith("data:"):
                continue
            chunk = line[5:].strip()
            if chunk == "[DONE]":
                break
            try:
                data = json.loads(chunk)
            except json.JSONDecodeError:
                continue
            etype = data.get("type")
            if etype == "error":
                return _fail(result, f"stream error event: {chunk[:400]}")
            if etype == "message_start":
                msg = data.get("message") or {}
                result["model"] = msg.get("model")
                u = msg.get("usage") or {}
                result["input_tokens"] = u.get("input_tokens")
                if u.get("output_tokens") is not None:
                    result["output_tokens"] = u.get("output_tokens")
            elif etype == "content_block_delta":
                now = time.monotonic()
                if first_event is None:
                    first_event = now  # first generated delta (text or thinking)
                last_event = now
                delta = data.get("delta") or {}
                if delta.get("type") in (None, "text_delta"):
                    parts.append(delta.get("text", ""))
            elif etype == "message_delta":
                last_event = time.monotonic()
                u = data.get("usage") or {}
                if u.get("output_tokens") is not None:
                    result["output_tokens"] = u["output_tokens"]  # cumulative
                if u.get("input_tokens") is not None and result["input_tokens"] is None:
                    result["input_tokens"] = u["input_tokens"]
                result["stop_reason"] = (data.get("delta") or {}).get("stop_reason")
            elif etype == "message_stop":
                got_stop = True
        result["text"] = "".join(parts)
    if not got_stop and result["stop_reason"] is None:
        return _fail(result, "stream ended without message_delta/message_stop")
    result["ok"] = True
    if first_event is not None:
        result["ttft"] = first_event - start
        gen = (last_event or first_event) - first_event
        result["gen_time"] = gen
        n = result["output_tokens"]
        # Throughput excludes TTFT and needs real token counts from usage.
        if n and n > 1 and gen > 0.05:
            result["tps"] = (n - 1) / gen


# --- Self-identification heuristics ----------------------------------------

_OTHER = (r"(chat\s?gpt|gpt[-\s]?\d[\w.\-]*|gpt|openai|gemini|bard|google|"
          r"deepseek|qwen|tongyi|alibaba|llama|meta|mistral|grok|xai|kimi|moonshot|"
          r"glm|zhipu|ernie|baidu|doubao|bytedance)")
_SELF_CLAIM = [
    rf"\bi\s*(?:am|'m|’m)\s+(?:an?\s+)?(?:ai\s+)?(?:model\s+|assistant\s+)?(?:called\s+|named\s+)?{_OTHER}\b",
    rf"\bmy\s+name\s+is\s+{_OTHER}\b",
    rf"\b(?:i\s*(?:was|am|'m|’m)|i've\s+been)\s+(?:(?!not\b|never\b)\w+[,\s]+){{0,4}}(?:developed|created|built|trained|made)\s+by\s+{_OTHER}\b",
    rf"\bi\s*(?:am|'m|’m)\s+(?:a|an)\s+(?:large\s+)?language\s+model\s+(?:\w+\s+){{0,3}}by\s+{_OTHER}\b",
]
_BARE_NAME = re.compile(rf"^\W*{_OTHER}[\w.\-\s]{{0,25}}\W*$", re.I)
_CLAUDE_CLAIM = re.compile(r"\bclaude\b|\banthropic\b", re.I)


def claims_other_identity(text: str) -> Optional[str]:
    """Return the matched phrase if the text self-identifies as a non-Claude model.

    Merely mentioning OpenAI/GPT (e.g. "unlike GPT-4, I...") is not a claim.
    """
    t = text.strip().lower()
    for pat in _SELF_CLAIM:
        m = re.search(pat, t, re.I | re.M)
        if m:
            return m.group(0).strip()[:80]
    if len(t) <= 40 and _BARE_NAME.match(t):  # answer is just another model's name
        return t
    return None


def claims_claude(text: str) -> bool:
    return bool(_CLAUDE_CLAIM.search(text or ""))


def parse_year_month(text: str) -> Optional[tuple]:
    m = re.search(r"(20\d{2})[-./](\d{1,2})\b", text or "")
    if m and 1 <= int(m.group(2)) <= 12:
        return int(m.group(1)), int(m.group(2))
    months = ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
    m = re.search(r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s+(20\d{2})\b",
                  (text or "").lower())
    if m:
        return int(m.group(2)), months.index(m.group(1)) + 1
    return None


def month_index(ym: tuple) -> int:
    return ym[0] * 12 + (ym[1] - 1)
