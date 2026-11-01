"""Latency percentile tracker — track p50/p90/p95/p99 latencies over time."""
from __future__ import annotations


def calculate_percentiles(latencies: list[float]) -> dict:
    if not latencies:
        return {"samples": 0}
    s = sorted(latencies)
    n = len(s)
    return {"samples": n, "min": s[0], "max": s[-1],
            "avg": round(sum(s) / n, 1),
            "p50": s[n // 2], "p75": s[int(n * 0.75)],
            "p90": s[int(n * 0.9)], "p95": s[int(n * 0.95)],
            "p99": s[int(n * 0.99)]}


def compare_percentiles(baseline: dict, current: dict) -> dict:
    changes = {}
    for p in ["p50", "p90", "p95", "p99"]:
        if p in baseline and p in current:
            delta = round(current[p] - baseline[p], 1)
            pct = round(delta / max(baseline[p], 0.01) * 100, 1)
            changes[p] = {"baseline": baseline[p], "current": current[p],
                          "delta": delta, "pct_change": pct}
    regression = any(c["pct_change"] > 20 for c in changes.values())
    return {"changes": changes, "regression": regression}
