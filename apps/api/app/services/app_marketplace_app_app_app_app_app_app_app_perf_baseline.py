"""Performance baseline — establish and track performance baselines."""
from __future__ import annotations


def establish_baseline(measurements: list[float]) -> dict:
    if not measurements:
        return {"established": False}
    s = sorted(measurements)
    n = len(s)
    return {"established": True, "count": n,
            "avg": round(sum(s) / n, 2), "p50": s[n // 2],
            "p95": s[int(n * 0.95)], "p99": s[int(min(n * 0.99, n - 1))],
            "min": s[0], "max": s[-1]}


def compare_to_baseline(baseline: dict, current: dict) -> dict:
    comparisons = {}
    for metric in ("avg", "p50", "p95", "p99"):
        b = baseline.get(metric, 0)
        c = current.get(metric, 0)
        delta = round(c - b, 2)
        pct = round(delta / max(abs(b), 0.01) * 100, 1)
        regression = pct > 10
        comparisons[metric] = {"baseline": b, "current": c, "delta": delta,
                                 "pct_change": pct, "regression": regression}
    has_regression = any(c["regression"] for c in comparisons.values())
    return {"comparisons": comparisons, "has_regression": has_regression}
