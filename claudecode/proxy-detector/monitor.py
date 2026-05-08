#!/usr/bin/env python3
"""
Claude Proxy Consistency Monitor

Catches intermittent model mixing by sending repeated requests and
detecting outliers. A dishonest proxy might serve real Claude 90% of
the time but secretly route some requests to cheaper models (DeepSeek,
GPT-3.5, Qwen) to cut costs.

This tool sends N identical requests and analyzes:
  - Response time distribution (outliers = different model)
  - Output token speed (TPS) variance
  - Style/content consistency
  - Knowledge cutoff consistency

Usage:
    python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 20
    python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 50 --interval 5
"""

import argparse
import time
import json
import statistics
import re
import sys
from typing import Optional
from datetime import datetime

try:
    import httpx
except ImportError:
    print("Please install httpx: pip install httpx")
    exit(1)


PROBE_PROMPTS = {
    "cutoff": {
        "prompt": "What is your knowledge cutoff date? Reply with ONLY YYYY-MM. Nothing else.",
        "system": "",
        "max_tokens": 20,
    },
    "identity": {
        "prompt": "What is your model name? Reply in one short sentence only.",
        "system": "",
        "max_tokens": 50,
    },
    "reasoning": {
        "prompt": (
            "A bat and ball cost $1.10 total. The bat costs $1.00 more than the ball. "
            "How much does the ball cost? Show your reasoning step by step."
        ),
        "system": None,
        "max_tokens": 300,
    },
    "style": {
        "prompt": "Explain what an API proxy is in exactly 3 sentences.",
        "system": None,
        "max_tokens": 200,
    },
}


def call_api(base_url: str, api_key: str, prompt: str, model: str,
             max_tokens: int = 300, system: Optional[str] = None) -> dict:
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
    if system is not None:
        body["system"] = system

    start = time.time()
    try:
        with httpx.Client(timeout=90) as client:
            resp = client.post(f"{base_url}/messages", headers=headers, json=body)
        elapsed = time.time() - start

        if resp.status_code == 200:
            data = resp.json()
            text = data["content"][0]["text"] if data.get("content") else ""
            usage = data.get("usage", {})
            output_tokens = usage.get("output_tokens", len(text.split()))
            tps = output_tokens / max(elapsed, 0.01)
            return {
                "status": 200,
                "elapsed": elapsed,
                "tps": tps,
                "text": text,
                "model": data.get("model", "unknown"),
                "output_tokens": output_tokens,
            }
        else:
            return {"status": resp.status_code, "elapsed": elapsed,
                    "text": "", "error": resp.text, "tps": 0}
    except Exception as e:
        return {"status": 0, "elapsed": time.time() - start,
                "text": "", "error": str(e), "tps": 0}


def detect_outliers(values: list, threshold: float = 2.0) -> list:
    """Find outliers using IQR method."""
    if len(values) < 4:
        return []
    sorted_v = sorted(values)
    q1 = sorted_v[len(sorted_v) // 4]
    q3 = sorted_v[3 * len(sorted_v) // 4]
    iqr = q3 - q1
    lower = q1 - threshold * iqr
    upper = q3 + threshold * iqr
    return [i for i, v in enumerate(values) if v < lower or v > upper]


def analyze_text_consistency(texts: list) -> dict:
    """Detect style changes that suggest model switching."""
    if not texts:
        return {"consistent": True, "anomalies": []}

    avg_len = statistics.mean(len(t) for t in texts)
    anomalies = []

    for i, text in enumerate(texts):
        t_lower = text.lower()

        # Check for non-Claude identifiers leaking
        if any(w in t_lower for w in ["deepseek", "qwen", "gpt", "openai", "gemini", "llama"]):
            anomalies.append({"round": i, "type": "identity_leak",
                              "detail": f"Non-Claude identifier in response"})

        # Check for dramatic length change (>3x or <0.3x average)
        if avg_len > 0:
            ratio = len(text) / avg_len
            if ratio > 3.0 or ratio < 0.3:
                anomalies.append({"round": i, "type": "length_anomaly",
                                  "detail": f"Length {len(text)} vs avg {avg_len:.0f} (ratio {ratio:.1f}x)"})

        # Check for Chinese when not expected (DeepSeek tends to default to Chinese)
        chinese_chars = len(re.findall(r'[一-鿿]', text))
        if chinese_chars > 5 and "chinese" not in PROBE_PROMPTS.get("style", {}).get("prompt", "").lower():
            anomalies.append({"round": i, "type": "language_switch",
                              "detail": f"Unexpected Chinese characters ({chinese_chars} chars)"})

    return {"consistent": len(anomalies) == 0, "anomalies": anomalies}


def analyze_cutoff_consistency(responses: list) -> dict:
    """Check if knowledge cutoff answers are consistent."""
    dates = []
    for r in responses:
        match = re.search(r"20\d{2}[-./]\d{2}", r.get("text", ""))
        if match:
            dates.append(match.group().replace("/", "-").replace(".", "-"))

    if not dates:
        return {"consistent": False, "detail": "Could not parse any cutoff dates"}

    unique_dates = set(dates)
    if len(unique_dates) == 1:
        return {"consistent": True, "date": dates[0], "detail": f"All {len(dates)} responses: {dates[0]}"}
    else:
        from collections import Counter
        counts = Counter(dates)
        return {
            "consistent": False,
            "dates": dict(counts),
            "detail": f"INCONSISTENT cutoffs: {dict(counts)} — different models detected!",
        }


def run_monitor(proxy_url: str, proxy_key: str, model: str,
                rounds: int = 20, interval: float = 1.0) -> dict:
    print(f"\n{'='*60}")
    print(f"  Claude Proxy Consistency Monitor")
    print(f"  Target: {proxy_url}")
    print(f"  Model:  {model}")
    print(f"  Rounds: {rounds} (interval: {interval}s)")
    print(f"  Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")

    results_by_type = {k: [] for k in PROBE_PROMPTS}
    all_latencies = []
    all_tps = []

    total_requests = rounds * len(PROBE_PROMPTS)
    current = 0

    for i in range(rounds):
        print(f"  Round {i+1}/{rounds}", end="")
        round_results = {}

        for probe_name, probe in PROBE_PROMPTS.items():
            current += 1
            r = call_api(
                proxy_url, proxy_key,
                probe["prompt"], model,
                max_tokens=probe["max_tokens"],
                system=probe.get("system"),
            )
            results_by_type[probe_name].append(r)
            all_latencies.append(r.get("elapsed", 0))
            all_tps.append(r.get("tps", 0))
            round_results[probe_name] = r

        # Print summary for this round
        latency = statistics.mean(r.get("elapsed", 0) for r in round_results.values())
        tps_avg = statistics.mean(r.get("tps", 0) for r in round_results.values())
        cutoff_text = round_results["cutoff"].get("text", "?")[:10]
        print(f"  | latency={latency:.2f}s | tps={tps_avg:.0f} | cutoff={cutoff_text}")

        if i < rounds - 1 and interval > 0:
            time.sleep(interval)

    # Analysis
    print(f"\n{'='*60}")
    print("  ANALYSIS")
    print(f"{'='*60}\n")

    report = {"rounds": rounds, "total_requests": total_requests, "findings": []}

    # 1. Latency outliers
    latency_outliers = detect_outliers(all_latencies)
    if latency_outliers:
        pct = len(latency_outliers) / len(all_latencies) * 100
        report["findings"].append({
            "test": "latency_outliers",
            "severity": "high" if pct > 20 else "medium",
            "detail": f"{len(latency_outliers)}/{len(all_latencies)} requests ({pct:.0f}%) have anomalous latency",
        })
        print(f"  [WARN] Latency outliers: {len(latency_outliers)} requests have unusual timing")
        outlier_times = [all_latencies[i] for i in latency_outliers]
        normal_times = [t for i, t in enumerate(all_latencies) if i not in latency_outliers]
        print(f"         Normal avg: {statistics.mean(normal_times):.2f}s")
        print(f"         Outlier avg: {statistics.mean(outlier_times):.2f}s")
        print(f"         Ratio: {statistics.mean(outlier_times)/max(statistics.mean(normal_times),0.01):.1f}x")
    else:
        print(f"  [OK] Latency consistent (avg={statistics.mean(all_latencies):.2f}s, "
              f"stdev={statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0:.2f}s)")
        report["findings"].append({
            "test": "latency_outliers", "severity": "none",
            "detail": "Latency is consistent across all requests",
        })

    # 2. TPS outliers
    tps_outliers = detect_outliers(all_tps)
    if tps_outliers:
        pct = len(tps_outliers) / len(all_tps) * 100
        report["findings"].append({
            "test": "tps_outliers",
            "severity": "high" if pct > 20 else "medium",
            "detail": f"{len(tps_outliers)} requests have anomalous token speed",
        })
        print(f"  [WARN] TPS outliers: {len(tps_outliers)} requests have unusual speed")
        outlier_tps = [all_tps[i] for i in tps_outliers]
        normal_tps = [t for i, t in enumerate(all_tps) if i not in tps_outliers]
        if normal_tps:
            print(f"         Normal avg: {statistics.mean(normal_tps):.1f} tps")
        if outlier_tps:
            print(f"         Outlier avg: {statistics.mean(outlier_tps):.1f} tps")
    else:
        avg_tps = statistics.mean(all_tps) if all_tps else 0
        print(f"  [OK] Token speed consistent (avg={avg_tps:.1f} tps)")

    # 3. Knowledge cutoff consistency
    cutoff_analysis = analyze_cutoff_consistency(results_by_type["cutoff"])
    if cutoff_analysis["consistent"]:
        print(f"  [OK] Knowledge cutoff consistent: {cutoff_analysis.get('date', '?')}")
    else:
        print(f"  [FAIL] {cutoff_analysis['detail']}")
        report["findings"].append({
            "test": "cutoff_inconsistency",
            "severity": "critical",
            "detail": cutoff_analysis["detail"],
        })

    # 4. Text style consistency
    style_texts = [r.get("text", "") for r in results_by_type["style"]]
    style_analysis = analyze_text_consistency(style_texts)
    if style_analysis["consistent"]:
        print(f"  [OK] Response style consistent across {rounds} rounds")
    else:
        for a in style_analysis["anomalies"]:
            print(f"  [WARN] Round {a['round']}: {a['type']} — {a['detail']}")
        report["findings"].append({
            "test": "style_inconsistency",
            "severity": "high",
            "detail": f"{len(style_analysis['anomalies'])} style anomalies detected",
            "anomalies": style_analysis["anomalies"],
        })

    # 5. Identity consistency
    identity_texts = [r.get("text", "").lower() for r in results_by_type["identity"]]
    identity_mentions_claude = sum(1 for t in identity_texts if "claude" in t)
    identity_mentions_other = sum(1 for t in identity_texts
                                  if any(w in t for w in ["deepseek", "gpt", "qwen", "gemini", "llama"]))
    if identity_mentions_other > 0:
        print(f"  [FAIL] Identity leaks: {identity_mentions_other}/{rounds} responses mention non-Claude models")
        report["findings"].append({
            "test": "identity_leak",
            "severity": "critical",
            "detail": f"{identity_mentions_other} responses identified as non-Claude model",
        })
    else:
        print(f"  [OK] Identity consistent: {identity_mentions_claude}/{rounds} identify as Claude")

    # Verdict
    critical = sum(1 for f in report["findings"] if f["severity"] == "critical")
    high = sum(1 for f in report["findings"] if f["severity"] == "high")
    medium = sum(1 for f in report["findings"] if f["severity"] == "medium")

    print(f"\n{'='*60}")
    if critical > 0:
        verdict = "MODEL MIXING DETECTED — proxy is routing to different models"
        mixing_pct = max(
            len(latency_outliers) / max(len(all_latencies), 1),
            len(tps_outliers) / max(len(all_tps), 1),
            identity_mentions_other / max(rounds, 1),
        ) * 100
        print(f"  VERDICT: {verdict}")
        print(f"  Estimated mixing rate: ~{mixing_pct:.0f}% of requests")
    elif high > 0:
        verdict = "SUSPICIOUS — possible intermittent model mixing"
        print(f"  VERDICT: {verdict}")
    else:
        verdict = "CONSISTENT — no model mixing detected in {rounds} rounds"
        print(f"  VERDICT: {verdict}")
    print(f"{'='*60}\n")

    report["verdict"] = verdict
    report["stats"] = {
        "avg_latency": statistics.mean(all_latencies),
        "stdev_latency": statistics.stdev(all_latencies) if len(all_latencies) > 1 else 0,
        "avg_tps": statistics.mean(all_tps) if all_tps else 0,
        "latency_outlier_count": len(latency_outliers),
        "tps_outlier_count": len(tps_outliers),
    }
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor a Claude proxy for intermittent model mixing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick check (20 rounds, ~2 minutes)
  python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx

  # Thorough check (50 rounds, spaced out)
  python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 50 --interval 5

  # Rush mode (no delay between requests)
  python monitor.py --proxy-url https://proxy.com/v1 --proxy-key sk-xxx --rounds 30 --interval 0
        """,
    )
    parser.add_argument("--proxy-url", required=True,
                        help="Proxy API base URL")
    parser.add_argument("--proxy-key", required=True,
                        help="API key for the proxy")
    parser.add_argument("--model", default="claude-sonnet-4-6-20250514",
                        help="Model to test")
    parser.add_argument("--rounds", type=int, default=20,
                        help="Number of test rounds (default: 20)")
    parser.add_argument("--interval", type=float, default=1.0,
                        help="Seconds between rounds (default: 1.0)")
    args = parser.parse_args()

    report = run_monitor(args.proxy_url, args.proxy_key, args.model,
                         args.rounds, args.interval)

    output_file = "monitor_report.json"
    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    print(f"Report saved to: {output_file}")
