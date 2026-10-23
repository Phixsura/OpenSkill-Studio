"""Rollup metrics aggregator — aggregate raw metrics into time buckets."""
from __future__ import annotations
import math


def rollup(data_points: list[dict], *, bucket_minutes: int = 5) -> dict:
    buckets: dict[int, list[float]] = {}
    for dp in data_points:
        ts = dp.get("timestamp", 0)
        value = dp.get("value", 0)
        bucket_key = (ts // (bucket_minutes * 60)) * (bucket_minutes * 60)
        buckets.setdefault(bucket_key, []).append(value)
    result = []
    for bk in sorted(buckets):
        vals = buckets[bk]
        n = len(vals)
        mean = sum(vals) / n
        sorted_vals = sorted(vals)
        p95_idx = min(int(n * 0.95), n - 1)
        result.append({
            "bucket": bk, "count": n,
            "min": round(min(vals), 2), "max": round(max(vals), 2),
            "avg": round(mean, 2), "sum": round(sum(vals), 2),
            "p95": round(sorted_vals[p95_idx], 2),
        })
    return {"buckets": result, "total_points": len(data_points),
            "bucket_count": len(result), "bucket_minutes": bucket_minutes}


def compute_rate(data_points: list[dict], *, window_sec: int = 60) -> dict:
    if len(data_points) < 2:
        return {"rate": 0, "error": "Need at least 2 points"}
    timestamps = sorted(dp.get("timestamp", 0) for dp in data_points)
    duration = timestamps[-1] - timestamps[0]
    if duration <= 0:
        return {"rate": 0, "duration": 0}
    rate = len(data_points) / (duration / window_sec)
    return {"rate": round(rate, 2), "duration": duration,
            "rate_display": f"{rate:.1f}/min" if window_sec == 60 else f"{rate:.1f}/{window_sec}s"}
