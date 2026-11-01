"""API endpoint performance baseline — establish and compare against baselines."""
from __future__ import annotations


def establish_baseline(endpoint: str, latencies: list[float]) -> dict:
    if not latencies:
        return {"endpoint": endpoint, "established": False}
    s = sorted(latencies)
    n = len(s)
    return {"endpoint": endpoint, "established": True, "samples": n,
            "p50": s[n // 2], "p95": s[int(n * 0.95)], "p99": s[int(n * 0.99)],
            "avg": round(sum(s) / n, 1), "min": s[0], "max": s[-1]}


def compare_to_baseline(baseline: dict, current: dict) -> dict:
    if not baseline.get("established"):
        return {"comparable": False}
    p99_change = round((current.get("p99", 0) - baseline["p99"]) / max(baseline["p99"], 0.01) * 100, 1)
    avg_change = round((current.get("avg", 0) - baseline["avg"]) / max(baseline["avg"], 0.01) * 100, 1)
    regression = p99_change > 20 or avg_change > 30
    return {"comparable": True, "p99_change_pct": p99_change, "avg_change_pct": avg_change,
            "regression": regression,
            "verdict": "regression" if regression else ("improved" if p99_change < -10 else "stable")}
