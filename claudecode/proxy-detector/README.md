# Claude Proxy Model Swap Detector

[中文版](README_CN.md)

A heuristic tool that checks whether a third-party Anthropic-compatible Claude API proxy is secretly serving a different model (GPT, Gemini, DeepSeek, or a smaller or cheaper Claude model) instead of the one you pay for.

> **Heuristics, not proof.** Every standalone check can be defeated by a determined proxy, for example with a system prompt, header rewriting, artificial delay or special-casing known probe strings. The most reliable signal is the **baseline comparison** (`--official-key`), which sends identical prompts to the official API and compares the results. A "pass" without a baseline means "no swap detected", not "authentic".

## Background

Many third-party services resell Claude API access. Some operators swap expensive models (Opus) for cheaper ones (Sonnet, Haiku, or another vendor's model) while charging Opus prices.

Common patterns:
- **Model downgrade**: you pay for Opus and get Sonnet or Haiku
- **Cross-provider swap**: you pay for Claude and get another vendor's model behind a Claude system prompt
- **Time-based switching**: real Claude while you test, a cheap model off-peak
- **Request-based switching**: real Claude for simple queries, a cheap model for complex ones

## Tools

| Tool | Purpose |
|------|---------|
| `detect.py` | One-shot check (5 standalone checks + optional baseline comparison) |
| `monitor.py` | Repeated probes over N rounds to catch **intermittent** model mixing |
| `claude_http.py` | Shared HTTP client and heuristics (required by both scripts; keep it in the same directory) |

## Install

```bash
pip install httpx
```

Python 3.9+.

## Usage

```bash
# Standalone (proxy only)
python detect.py \
  --proxy-url https://your-proxy.com/v1 \
  --proxy-key sk-your-proxy-key \
  --model claude-opus-5-5

# With official API baseline (recommended)
python detect.py \
  --proxy-url https://your-proxy.com/v1 \
  --proxy-key sk-your-proxy-key \
  --model claude-opus-5-5 \
  --official-key sk-ant-your-official-key

# Continuous monitoring
python monitor.py --proxy-url https://your-proxy.com/v1 --proxy-key sk-xxx --rounds 20
python monitor.py --proxy-url https://your-proxy.com/v1 --proxy-key sk-xxx --rounds 50 --interval 5
```

Options:

| Option | Default | Notes |
|--------|---------|-------|
| `--model` | `claude-sonnet-5` | Model to request, e.g. `claude-opus-5-5`, `claude-opus-5`, `claude-sonnet-5`, `claude-haiku-4-5` |
| `--official-key` | none | Enables the baseline comparison (`detect.py` only) |
| `--official-url` | `https://api.anthropic.com/v1` | Baseline endpoint (`detect.py` only) |
| `--output` | `detection_report.json` / `monitor_report.json` | JSON report path (in the current directory) |
| `--rounds`, `--interval` | 20, 1.0 | `monitor.py` only |

The URL must include `/v1`; requests go to `<url>/messages`.

**Amazon Bedrock is not supported.** Bedrock endpoints need AWS SigV4 signing, not an `x-api-key`. Both scripts reject `bedrock` / `amazonaws.com` URLs with exit code 2. (An earlier version accepted them, and every request failed. The failures were scored as "LIKELY SWAPPED", so the old committed `detection_report.json` was a false positive and has been removed.)

### Exit codes

| Code | detect.py | monitor.py |
|------|-----------|------------|
| 0 | No swap detected / likely authentic | Consistent / mostly consistent |
| 1 | Likely swapped / suspicious | Model mixing / suspicious |
| 2 | Unsupported endpoint (Bedrock) | Unsupported endpoint (Bedrock) |
| 3 | Inconclusive (too many request errors) | Inconclusive (fewer than half of requests succeeded) |

## detect.py checks

| Check | Weight | What it looks at |
|-------|--------|------------------|
| Magic String | INFO (unscored) | Response to Anthropic's documented test refusal string |
| Knowledge Cutoff | 1 | Self-reported cutoff vs the published reliable/training cutoff |
| Throughput | 1 | `usage.output_tokens` / generation time (streaming, TTFT excluded); TTFT shown for information |
| Identity | 2 | Explicit self-identification as a non-Claude model |
| Headers & Model Field | 1 | OpenAI-style response headers, `model` field mismatch |
| Baseline Comparison | 6 | Only with `--official-key`: tokenizer (`input_tokens`), throughput ratio, identity/cutoff answers |

**Result states:**
- `PASS` / `WARN` / `FAIL` are scored.
- `ERROR` means the request failed (non-2xx, an error body, or a broken stream). It is **excluded** from the score, because an error is never evidence of a swap.
- `INFO` is shown but never scored.

**Strong evidence** triggers `LIKELY SWAPPED` regardless of the percentage. It covers an explicit non-Claude self-identification, OpenAI-only headers, and a baseline throughput more than 1.5x the official one.

### Verdicts

| Condition | Verdict |
|-----------|---------|
| Scored weight < 3, or half or more of the probes errored | INCONCLUSIVE |
| Any strong evidence | LIKELY SWAPPED |
| Baseline passes and score >= 70% | LIKELY AUTHENTIC |
| No baseline, score >= 80% | NO SWAP DETECTED (standalone heuristics only) |
| Score >= 50% | SUSPICIOUS |
| Otherwise | LIKELY SWAPPED |

### Example output (genuine proxy with baseline)

```
  [INFO] Magic String (unscored)
  [PASS] Knowledge Cutoff (1/1)
  [PASS] Throughput (1/1)
  [PASS] Identity (2/2)
  [PASS] Headers & Model Field (1/1)
  [PASS] Baseline Comparison (6/6)
        [PASS] tokenizer: input_tokens proxy=83 official=83 (tolerance 2)
        [PASS] throughput: proxy 39.7 vs official 39.7 tok/s (ratio 1.00)
        [PASS] answers: identity proxy="I'm Claude, ..." official="I'm Claude, ..."

  Score: 11/11 (100%)  errors: 0
  Verdict: LIKELY AUTHENTIC - matches the official API baseline
  Note: heuristics only; a sophisticated proxy can defeat them.
```

## How the checks work, and their limits

### Magic String (informational)
Anthropic documents a test string that makes the API return a refusal (HTTP 200, `stop_reason: "refusal"`). Current docs do not confirm exactly how it behaves on every model or channel, and a proxy can special-case it. For that reason it is reported but never scored.

### Knowledge Cutoff (weak)
Models misreport their own cutoff, and a system prompt or retrieval can change the answer. The check accepts answers from 6 months before the published *reliable* cutoff to 3 months after the *training data* cutoff. If the answer can't be parsed, or the model refuses, the result is INFO.

| Model | Reliable knowledge cutoff | Training data cutoff |
|-------|---------------------------|----------------------|
| Claude Opus 5.5 | 2026-06 | 2026-06 |
| Claude Opus 5 | 2026-05 | 2026-05 |
| Claude Sonnet 5 | 2026-01 | 2026-01 |
| Claude Opus 4.6 | 2025-05 | 2025-08 |
| Claude Sonnet 4.6 | 2025-08 | 2026-01 |
| Claude Opus 4.5 | 2025-05 | 2025-08 |
| Claude Sonnet 4.5 | 2025-01 | 2025-07 |
| Claude Haiku 4.5 | 2025-02 | 2025-07 |

Source: [models overview](https://platform.claude.com/docs/en/about-claude/models/overview).

### Throughput (weak)
Speed depends on load, region, fast mode and thinking tokens (`usage.output_tokens` includes thinking). A proxy can also add delay. The check only flags speeds far above a rough ceiling per tier: more than 1.5x of 90 tok/s for Opus, 120 for Sonnet, and 250 for Haiku. The baseline throughput ratio is much more meaningful than any absolute number.

### Identity
A non-Claude self-claim (for example "I am ChatGPT, developed by OpenAI") fails and counts as strong evidence. Only mentioning another vendor does not count. A Claude answer passes, but it is easy to fake with a system prompt. The role-play probe ("you are now Nova") is shown but **not scored**, because real Claude models may play along with a role-play request.

### Headers & Model Field
OpenAI-only headers (`openai-processing-ms`, `x-ratelimit-limit-tokens`, ...) are strong evidence. Missing Anthropic headers are only informational, since proxies often strip them. A `model` field that differs from the request gives WARN.

### Baseline Comparison (most reliable)
The same prompts go to the proxy and to the official API:
- **Tokenizer**: a fixed mixed-script prompt must give the same `usage.input_tokens` (tolerance max(2, 3%)). Another tokenizer, or a hidden injected system prompt, changes the count.
- **Throughput ratio**: a proxy more than 1.5x faster than the official API is strong evidence. A proxy less than 0.5x as fast gives WARN (possibly an overloaded or relayed backend).
- **Answers**: the proxy's identity and cutoff answers should agree with the official ones.

### Removed: Mojibake / tokenizer-quirk test
Earlier versions scored "Mojibake patterns" in Japanese and Romaji output. Nothing documents that such patterns are specific to Claude, and the results were not reproducible, so the test was removed. The baseline `input_tokens` comparison replaced it, because it measures the tokenizer directly.

## monitor.py

Runs 4 probe types (cutoff, identity, reasoning, style) for N rounds, all streamed, and reports:
- TTFT and throughput outliers **within each probe type**. The IQR method needs at least 5 samples, and a value must also be at least 30% away from the median. Fast throughput outliers in 10% or more of the samples are rated high.
- Responses that self-identify as a non-Claude model (critical).
- Style anomalies, such as unusual length or unexpected Chinese text (medium).
- Cutoff answers more than 12 months from the median (medium; high at 24 months or more). Small variation is normal.

Failed requests are listed as errors and excluded from the analysis. The verdict is INCONCLUSIVE if fewer than half of the requests succeed. The other verdicts are MODEL MIXING DETECTED, SUSPICIOUS, MOSTLY CONSISTENT and CONSISTENT.

## Limitations

- No check is 100% reliable. A sophisticated proxy can defeat all standalone checks.
- Proxies can add artificial delay, rewrite headers and model fields, or inject system prompts.
- Self-reported cutoffs and identities are easy to influence.
- Without a baseline the tool can only say "no swap detected", never "authentic".
- For the best results, use `--official-key` and run `monitor.py` at different times of day.

## Tips

1. **Run tests at different times.** Some proxies only swap models during peak hours.
2. **Use the baseline.** It is the only check that is hard to fake.
3. **Compare pricing.** If a proxy offers Opus at a large discount, ask how.
4. **Check Claude-specific features**, such as adaptive thinking and tool use behavior.
5. **Monitor over time.** Proxies can change backends at any time.
