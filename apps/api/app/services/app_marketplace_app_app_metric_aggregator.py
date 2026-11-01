"""Metric aggregator — time-series metric aggregation."""

import math
from collections import defaultdict


def aggregate_metrics(*, data_points: list[dict], interval: str = "1h") -> dict:
    buckets: dict[str, list[float]] = defaultdict(list)
    for dp in data_points:
        ts = dp.get("timestamp", "")[:13]  # truncate to hour
        val = dp.get("value", 0)
        buckets[ts].append(val)
    aggregated = []
    for ts in sorted(buckets):
        vals = buckets[ts]
        aggregated.append({
            "timestamp": ts,
            "count": len(vals),
            "sum": round(sum(vals), 2),
            "avg": round(sum(vals) / len(vals), 2),
            "min": round(min(vals), 2),
            "max": round(max(vals), 2),
        })
    all_vals = [dp.get("value", 0) for dp in data_points]
    return {"buckets": aggregated, "bucket_count": len(aggregated),
            "interval": interval, "total_points": len(data_points),
            "global_avg": round(sum(all_vals) / max(len(all_vals), 1), 2),
            "global_min": round(min(all_vals), 2) if all_vals else 0,
            "global_max": round(max(all_vals), 2) if all_vals else 0}


def percentile(*, values: list[float], p: float) -> float:
    if not values:
        return 0
    s = sorted(values)
    k = (len(s) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return round(s[f] * (c - k) + s[c] * (k - f), 2)
