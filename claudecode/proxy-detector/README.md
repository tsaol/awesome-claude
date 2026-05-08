# Claude Proxy Model Swap Detector

[中文版](README_CN.md)

A tool to detect if a third-party Claude API proxy is secretly serving a different model (GPT-4, Gemini, or a smaller/cheaper Claude model) instead of what you're paying for.

## Background

The Claude API relay/proxy market has exploded — over 100+ third-party services now claim to provide Claude access. Research shows that some proxy operators swap expensive models (Opus) with cheaper ones (Sonnet, Haiku, or even GPT-3.5) to increase their profit margin, while charging Opus prices.

Common scam patterns observed in the wild:
- **Model downgrade**: You pay for Opus, you get Sonnet or Haiku
- **Cross-provider swap**: You pay for Claude, you get GPT-4-mini with a Claude system prompt
- **Time-based switching**: Real Claude during testing hours, cheap model during off-peak
- **Request-based switching**: Real Claude for simple queries, cheap model for complex ones

## How It Works

The detector runs 6 levels of verification, inspired by the "defense in depth" approach:

| Level | Test | What It Detects |
|-------|------|-----------------|
| 1 | **Magic String** | Official Anthropic channel vs proxy (channel fingerprint) |
| 2 | **Knowledge Cutoff** | Model generation via temporal anchor (hardest to fake) |
| 3 | **Latency & TPS** | Model size via physics — Opus cannot be fast (unfakeable) |
| 4 | **Identity & Refusal** | Behavioral patterns specific to Claude |
| 5 | **Tokenizer Signature** | Model-specific encoding quirks (Mojibake patterns) |
| 6 | **Headers & Model Field** | API response metadata |

### Why These Tests Work

**Physics cannot be faked.** A large model (Opus, ~2T parameters) physically cannot produce tokens as fast as a small model (Haiku). If you request Opus but get responses in <1 second with 85+ tokens/sec, it's not Opus.

**Memory boundaries are hard to forge.** Each model has a specific training cutoff date baked into its weights during pre-training. System prompts can change a model's "personality" but cannot perfectly fake knowledge boundaries. Asking without a system prompt forces the model to reveal its true temporal anchor.

**The Magic String** is an undocumented Anthropic mechanism where a specific hash string triggers a refusal on official channels. Proxies that simply forward requests to non-Anthropic backends won't trigger this behavior.

## Install

```bash
pip install httpx
```

## Usage

### Basic test (proxy only)

```bash
python detect.py \
  --proxy-url https://your-proxy.com/v1 \
  --proxy-key sk-your-proxy-key \
  --model claude-opus-4-6-20250514
```

### With official API baseline

```bash
python detect.py \
  --proxy-url https://your-proxy.com/v1 \
  --proxy-key sk-your-proxy-key \
  --model claude-opus-4-6-20250514 \
  --official-key sk-ant-your-official-key
```

## Output

```
============================================================
  Claude Proxy Model Swap Detector v2
  Target: https://some-proxy.com/v1
  Model:  claude-opus-4-6-20250514
============================================================

[1/6] Testing magic string (channel fingerprint)...
  Result: WARN
[2/6] Testing knowledge cutoff (temporal anchor)...
  Response: 2025-03
[3/6] Testing latency & tokens-per-second (physics fingerprint)...
  TTFT: 2.31s, TPS: 32.4, Total: 8.72s
[4/6] Testing model identity & refusal behavior...
  Identity: i am claude, made by anthropic...
  Refusal: i'm claude and i'll continue to be claude...
[5/6] Testing tokenizer signature (Mojibake detection)...
  Japanese: True, Romaji: True, Mojibake: False
[6/6] Testing response headers & model field...
  Model field: claude-opus-4-6-20250514

============================================================
  RESULTS
============================================================

  [WARN] Magic String (1/2)
  [PASS] Knowledge Cutoff (2/2)
  [PASS] Latency & TPS (2/2)
  [PASS] Identity & Refusal (2/2)
  [PASS] Tokenizer Signature (1/1)
  [PASS] Headers & Model Field (1/1)

============================================================
  Score: 9/10 (90%)
  Verdict: LIKELY AUTHENTIC — probably real Claude
============================================================
```

### Verdict Scale

| Score | Verdict | Meaning |
|-------|---------|---------|
| 80-100% | LIKELY AUTHENTIC | Probably real Claude |
| 50-79% | SUSPICIOUS | Possible model mixing or downgrade |
| 0-49% | LIKELY SWAPPED | Probably NOT the claimed model |

## Detection Techniques Explained

### Level 1: Magic String (Channel Fingerprint)

Anthropic's official API intercepts requests containing a specific magic hash string and returns a structured refusal. Third-party proxies forwarding to non-Anthropic backends will either:
- Pass the request through (model responds normally) → NOT official
- Return an empty response → inconclusive
- Return the official refusal → likely official channel

### Level 2: Knowledge Cutoff (Temporal Anchor)

Each Claude model has a specific knowledge cutoff embedded in its weights:

| Model | Expected Cutoff |
|-------|----------------|
| Claude Opus 4.6 | 2025-03 |
| Claude Sonnet 4.6 | 2025-02 |
| Claude Haiku 4.5 | 2025-03 |
| Claude Sonnet 4.5 | 2025-02 |
| Claude Opus 4.5 | 2025-02 |
| Claude Sonnet 4 | 2025-02 |

The test sends the request with an **empty system prompt** (`system: ""`) to strip any proxy-injected persona. If you request Opus 4.6 but get a cutoff of "2024-10", you're likely getting an older Sonnet.

### Level 3: Latency & TPS (Physics Fingerprint)

Model size dictates speed. These are physical constraints that cannot be faked:

| Model | Expected TTFT | Expected TPS |
|-------|--------------|-------------|
| Opus | 1.5-3.0s | 25-45 tokens/s |
| Sonnet 4.6 | 0.8-2.0s | 30-55 tokens/s |
| Haiku | 0.2-0.5s | 100-200 tokens/s |

Real Bedrock baseline for Sonnet 4.6 (10 rounds):
- Latency: 4.31s avg (stdev 1.12s) for ~155 token output
- TPS: 37.3 avg (range 20-42)
- Cutoff: "2025-02" (8/10 consistent)

**Key insight**: If your "Opus" responds with TTFT < 1s and TPS > 80, it's physically impossible for it to be Opus. This is the hardest test to cheat — you'd need to artificially add delay, but that costs the proxy operator money.

Real-world data from pressure testing (source: cnblogs.com/sprinng):

| Metric | Official Opus | Official Sonnet | Fake "Opus" (actually Sonnet) |
|--------|--------------|-----------------|-------------------------------|
| TTFT | ~1.5-2.5s | ~0.6-1.0s | 0.7s (too fast!) |
| TPS | ~25-40 | ~70-100 | 85 (Sonnet speed) |
| Complex reasoning | 92/100 | 85/100 | 58/100 |
| Knowledge cutoff | 2025-03 | 2025-03 | 2024-10 (busted) |

### Level 4: Identity & Refusal (Behavioral Fingerprint)

Claude has specific behavioral patterns:
- Identifies itself as Claude/Anthropic
- Refuses to pretend to be other AI systems
- Has a distinctive writing style

These are the weakest signals (easy to fake with system prompts) but still useful as one data point.

### Level 5: Tokenizer Signature (Mojibake Detection)

Different models have different tokenizers that produce characteristic encoding artifacts when handling multilingual text. Claude has specific patterns with Japanese characters + Romaji combinations.

### Level 6: Headers & Model Field

The official Anthropic API returns specific headers (`x-request-id`, `anthropic-ratelimit-*`). OpenAI-compatible proxies may leak `x-ratelimit-limit-tokens` or other OpenAI-style headers.

## Limitations

- No single test is 100% reliable
- Sophisticated proxies may add artificial delays to mimic Opus speed
- Magic string detection may evolve as Anthropic updates their API
- Knowledge cutoff can be partially spoofed with RAG
- Best results: combine all tests + run multiple times at different hours

## Tips for Users

1. **Run tests at different times** — some proxies only swap models during peak hours
2. **Test complex reasoning** — simple questions don't reveal model differences
3. **Compare pricing** — if a proxy offers Opus at 80% discount, question how
4. **Check if extended thinking works** — Claude-specific features can't be faked by GPT
5. **Monitor over time** — run weekly checks, as proxies may change backend models

