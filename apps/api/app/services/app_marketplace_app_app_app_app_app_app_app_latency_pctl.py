"""Latency percentile tracker — compute p50/p90/p95/p99 latencies."""
from __future__ import annotations
import math


def compute_percentiles(latencies: list[float]) -> dict:
    if not latencies:
        return {"count": 0, "p50": 0, "p90": 0, "p95": 0, "p99": 0, "avg": 0, "max": 0}
    s = sorted(latencies)
    n = len(s)
    p50 = s[int(n * 0.50)]
    p90 = s[int(min(n * 0.90, n - 1))]
    p95 = s[int(min(n * 0.95, n - 1))]
    p99 = s[int(min(n * 0.99, n - 1))]
    avg = round(sum(s) / n, 2)
    return {"count": n, "p50": p50, "p90": p90, "p95": p95, "p99": p99,
            "avg": avg, "min": s[0], "max": s[-1]}


def check_slo(percentiles: dict, targets: dict) -> dict:
    violations = []
    for metric, target in targets.items():
        actual = percentiles.get(metric, 0)
        if actual > target:
            violations.append({"metric": metric, "actual": actual, "target": target,
                               "over_by": round(actual - target, 2)})
    return {"met": len(violations) == 0, "violations": violations,
            "checked": len(targets)}


def bucket_latencies(latencies: list[float], buckets: list[float]) -> dict:
    counts = {f"<={b}ms": 0 for b in buckets}
    counts[f">{buckets[-1]}ms"] = 0
    for l in latencies:
        placed = False
        for b in buckets:
            if l <= b:
                counts[f"<={b}ms"] += 1
                placed = True
                break
        if not placed:
            counts[f">{buckets[-1]}ms"] += 1
    return {"buckets": counts, "total": len(latencies)}
