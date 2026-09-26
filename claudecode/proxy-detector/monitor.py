#!/usr/bin/env python3
"""
Claude Proxy Consistency Monitor

Heuristically catches intermittent model mixing by sending repeated probes
and looking for outliers. A dishonest proxy might serve real Claude most of
the time but route some requests to a cheaper model.

Analysis (per probe type, successful requests only):
  - Time to first token and generation throughput (usage.output_tokens / s,
    TTFT excluded) outliers, compared only within the same probe type
  - Explicit self-identification as a non-Claude model (critical)
  - Style anomalies (length, unexpected language)
  - Self-reported cutoff spread (only large spreads are flagged; models
    misreport their cutoff, so small variation is normal)

Failed requests (non-2xx, error bodies, broken streams) are reported as
errors and excluded - they are never counted as model mixing.

Usage:
    python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 20
    python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 50 --interval 5
"""

import argparse
import json
import re
import statistics
import sys
import time
from datetime import datetime

from claude_http import (call_api, claims_claude, claims_other_identity,
                         month_index, parse_year_month)

DEFAULT_MODEL = "claude-sonnet-5"

PROBE_PROMPTS = {
    "cutoff": {
        "prompt": "What is your knowledge cutoff date? Reply with ONLY YYYY-MM. Nothing else.",
        "max_tokens": 1024,
    },
    "identity": {
        "prompt": "What model are you, and which company created you? Reply in one short sentence.",
        "max_tokens": 1024,
    },
    "reasoning": {
        "prompt": (
            "A bat and ball cost $1.10 total. The bat costs $1.00 more than the ball. "
            "How much does the ball cost? Show your reasoning step by step."
        ),
        "max_tokens": 1024,
    },
    "style": {
        "prompt": "Explain what an API proxy is in exactly 3 sentences.",
        "max_tokens": 1024,
    },
}
MIN_SAMPLES = 5


def detect_outliers(values: list, threshold: float = 2.0, min_rel: float = 0.3) -> list:
    """Indices of IQR outliers (needs MIN_SAMPLES values).

    A value must also differ from the median by at least ``min_rel`` (30%) so
    that tiny jitter on very stable timings is not reported.
    """
    if len(values) < MIN_SAMPLES:
        return []
    s = sorted(values)
    q1, q3 = s[len(s) // 4], s[3 * len(s) // 4]
    iqr = q3 - q1
    if iqr == 0:
        iqr = max(abs(statistics.median(s)) * 0.05, 1e-9)
    lo, hi = q1 - threshold * iqr, q3 + threshold * iqr
    med = statistics.median(s)
    return [i for i, v in enumerate(values)
            if (v < lo or v > hi) and abs(v - med) >= min_rel * abs(med)]


def analyze_text_consistency(items: list) -> list:
    """items: [(round, text)] for one probe type. Returns anomalies."""
    if not items:
        return []
    avg_len = statistics.mean(len(t) for _, t in items) or 1
    anomalies = []
    for rnd, text in items:
        claim = claims_other_identity(text)
        if claim:
            anomalies.append({"round": rnd, "type": "identity_claim", "severity": "critical",
                              "detail": f"Self-identifies as non-Claude: {claim!r}"})
        ratio = len(text) / avg_len
        if ratio > 3.0 or ratio < 0.3:
            anomalies.append({"round": rnd, "type": "length_anomaly", "severity": "medium",
                              "detail": f"Length {len(text)} vs avg {avg_len:.0f} ({ratio:.1f}x)"})
        cjk = len(re.findall(r"[一-鿿]", text))
        if cjk > 5:
            anomalies.append({"round": rnd, "type": "language_switch", "severity": "medium",
                              "detail": f"Unexpected Chinese characters ({cjk}) in an English prompt"})
    return anomalies


def analyze_cutoff_consistency(items: list) -> dict:
    """items: [(round, text)]. Flags only large spreads from the median answer."""
    parsed = [(rnd, parse_year_month(t)) for rnd, t in items]
    dated = [(rnd, ym) for rnd, ym in parsed if ym]
    if not dated:
        return {"severity": "none", "detail": "No parsable cutoff answers (not scored)"}
    med = statistics.median(month_index(ym) for _, ym in dated)
    far = [(rnd, ym) for rnd, ym in dated if abs(month_index(ym) - med) > 12]
    counts = {}
    for _, ym in dated:
        k = f"{ym[0]}-{ym[1]:02d}"
        counts[k] = counts.get(k, 0) + 1
    if not far:
        return {"severity": "none", "answers": counts,
                "detail": f"{len(dated)} answers within 12 months of the median: {counts}"}
    very_far = any(abs(month_index(ym) - med) >= 24 for _, ym in far)
    return {"severity": "high" if very_far else "medium", "answers": counts,
            "rounds": [r for r, _ in far],
            "detail": f"{len(far)} cutoff answers >12 months from the median: {counts} "
                      "(self-reports are unreliable; corroborate with other signals)"}


def run_monitor(proxy_url, proxy_key, model, rounds=20, interval=1.0) -> dict:
    print(f"\n{'='*60}")
    print("  Claude Proxy Consistency Monitor")
    print(f"  Target: {proxy_url}")
    print(f"  Model:  {model}")
    print(f"  Rounds: {rounds} (interval: {interval}s)")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    results = {k: [] for k in PROBE_PROMPTS}  # probe -> [(round, result)]
    for i in range(rounds):
        line = []
        for name, probe in PROBE_PROMPTS.items():
            r = call_api(proxy_url, proxy_key, probe["prompt"], model,
                         max_tokens=probe["max_tokens"], stream=True)
            results[name].append((i, r))
            if r["ok"]:
                tps = f"{r['tps']:.0f}" if r["tps"] else "-"
                line.append(f"{name}:ttft={r['ttft'] or 0:.2f}s,tps={tps}")
            else:
                line.append(f"{name}:ERROR({r['status']})")
        print(f"  Round {i+1}/{rounds} | " + " | ".join(line))
        if i < rounds - 1 and interval > 0:
            time.sleep(interval)

    print(f"\n{'='*60}\n  ANALYSIS\n{'='*60}\n")
    findings = []
    flagged_rounds = set()
    total = rounds * len(PROBE_PROMPTS)
    ok_items = {k: [(rnd, r) for rnd, r in v if r["ok"]] for k, v in results.items()}
    n_ok = sum(len(v) for v in ok_items.values())
    n_err = total - n_ok

    if n_err:
        by_status = {}
        for v in results.values():
            for _, r in v:
                if not r["ok"]:
                    by_status[r["status"]] = by_status.get(r["status"], 0) + 1
        findings.append({"test": "request_errors", "severity": "error",
                         "detail": f"{n_err}/{total} requests failed {by_status} - excluded "
                                   "from analysis (errors are not evidence of mixing)"})
        print(f"  [ERROR] {n_err}/{total} requests failed {by_status}; excluded")

    # 1+2. Timing outliers, per probe type.
    for metric in ("ttft", "tps"):
        for name, items in ok_items.items():
            vals = [(rnd, r[metric]) for rnd, r in items if r.get(metric)]
            idx = detect_outliers([v for _, v in vals])
            if not idx:
                continue
            out = [vals[j] for j in idx]
            normal = [v for j, (_, v) in enumerate(vals) if j not in idx]
            pct = len(idx) / len(vals) * 100
            # Faster-than-normal throughput is the interesting direction.
            fast = metric == "tps" and normal and statistics.mean(v for _, v in out) > statistics.mean(normal)
            sev = "high" if (fast and pct >= 10) else "medium"
            if fast:
                flagged_rounds.update(r for r, _ in out)
            findings.append({"test": f"{metric}_outliers[{name}]", "severity": sev,
                             "detail": f"{len(idx)}/{len(vals)} '{name}' requests anomalous {metric}: "
                                       f"outliers {[round(v, 2) for _, v in out]} vs normal avg "
                                       f"{statistics.mean(normal) if normal else 0:.2f}"})
            print(f"  [WARN] {metric} outliers in '{name}': {len(idx)}/{len(vals)}")

    # 3. Cutoff spread.
    cutoff = analyze_cutoff_consistency([(rnd, r["text"]) for rnd, r in ok_items["cutoff"]])
    if cutoff["severity"] != "none":
        findings.append({"test": "cutoff_spread", **cutoff})
        flagged_rounds.update(cutoff.get("rounds", []))
        print(f"  [WARN] {cutoff['detail']}")
    else:
        print(f"  [OK] Cutoff: {cutoff['detail']}")

    # 4. Style + identity claims across all text probes.
    anomalies = []
    for name, items in ok_items.items():
        texts = [(rnd, r["text"]) for rnd, r in items]
        a = analyze_text_consistency(texts) if name in ("style", "reasoning") else \
            [x for x in analyze_text_consistency(texts) if x["type"] == "identity_claim"]
        for x in a:
            x["probe"] = name
        anomalies += a
    crit = [a for a in anomalies if a["severity"] == "critical"]
    other = [a for a in anomalies if a["severity"] != "critical"]
    if crit:
        flagged_rounds.update(a["round"] for a in crit)
        findings.append({"test": "identity_claim", "severity": "critical",
                         "detail": f"{len(crit)} responses self-identify as a non-Claude model",
                         "anomalies": crit})
        print(f"  [FAIL] {len(crit)} responses self-identify as a non-Claude model")
    if other:
        findings.append({"test": "style_anomalies", "severity": "medium",
                         "detail": f"{len(other)} style anomalies", "anomalies": other})
        print(f"  [WARN] {len(other)} style anomalies")
    idents = [r["text"] for _, r in ok_items["identity"]]
    print(f"  [INFO] {sum(claims_claude(t) for t in idents)}/{len(idents)} identity answers mention Claude/Anthropic")

    # Verdict
    sev = [f["severity"] for f in findings]
    print(f"\n{'='*60}")
    if n_ok == 0 or n_ok < total / 2:
        verdict = f"INCONCLUSIVE - {n_err}/{total} requests failed; fix the endpoint/auth and retry"
    elif "critical" in sev:
        verdict = "MODEL MIXING DETECTED - some responses self-identify as a non-Claude model"
    elif "high" in sev:
        verdict = "SUSPICIOUS - possible intermittent model mixing"
    elif "medium" in sev:
        verdict = f"MOSTLY CONSISTENT - minor anomalies in {rounds} rounds (likely noise)"
    else:
        verdict = f"CONSISTENT - no model mixing detected in {rounds} rounds"
    print(f"  VERDICT: {verdict}")
    if flagged_rounds and not verdict.startswith("INCONCLUSIVE"):
        print(f"  Rounds with anomalies: {len(flagged_rounds)}/{rounds}")
    print("  Note: heuristics only; a sophisticated proxy can defeat them.")
    print(f"{'='*60}\n")

    def _avg(metric, name=None):
        vals = [r[metric] for k, v in ok_items.items() if name in (None, k)
                for _, r in v if r.get(metric)]
        return statistics.mean(vals) if vals else None

    return {
        "rounds": rounds, "total_requests": total, "ok_requests": n_ok,
        "error_requests": n_err, "findings": findings, "verdict": verdict,
        "flagged_rounds": sorted(flagged_rounds),
        "stats": {name: {"avg_ttft": _avg("ttft", name), "avg_tps": _avg("tps", name)}
                  for name in PROBE_PROMPTS},
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Monitor a Claude proxy for intermittent model mixing (heuristic)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick check (20 rounds)
  python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx

  # Thorough check (50 rounds, spaced out)
  python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 50 --interval 5

Amazon Bedrock endpoints (SigV4 auth) are not supported.
        """,
    )
    parser.add_argument("--proxy-url", required=True,
                        help="Proxy base URL including /v1 (requests go to <url>/messages)")
    parser.add_argument("--proxy-key", required=True, help="API key for the proxy")
    parser.add_argument("--model", default=DEFAULT_MODEL,
                        help=f"Model to test (default: {DEFAULT_MODEL})")
    parser.add_argument("--rounds", type=int, default=20, help="Number of rounds (default: 20)")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Seconds between rounds (default: 1.0)")
    parser.add_argument("--output", default="monitor_report.json",
                        help="Report path (default: ./monitor_report.json)")
    args = parser.parse_args(argv)

    if re.search(r"bedrock|amazonaws\.com", args.proxy_url, re.I):
        print("Amazon Bedrock endpoints require AWS SigV4 signing; not supported.",
              file=sys.stderr)
        return 2

    report = run_monitor(args.proxy_url, args.proxy_key, args.model, args.rounds, args.interval)
    with open(args.output, "w") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    print(f"Report saved to: {args.output}")
    # Exit codes: 0 consistent, 1 mixing/suspicious, 3 inconclusive.
    v = report["verdict"]
    return 3 if v.startswith("INCONCLUSIVE") else (1 if v.startswith(("MODEL MIXING", "SUSPICIOUS")) else 0)


if __name__ == "__main__":
    sys.exit(main())
