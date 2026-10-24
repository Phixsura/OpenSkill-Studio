"""Metric aggregator — aggregate time-series metrics with downsampling."""

import math


def aggregate_metrics(*, data_points: list[dict], interval_sec: int = 60,
                        aggregation: str = "avg") -> dict:
    if not data_points:
        return {"buckets": [], "total_points": 0}
    valid_aggs = {"avg", "sum", "min", "max", "count", "p95"}
    if aggregation not in valid_aggs:
        return {"error": f"Invalid aggregation. Valid: {', '.join(sorted(valid_aggs))}"}
    buckets: dict[int, list[float]] = {}
    for dp in data_points:
        ts = dp.get("timestamp", 0)
        bucket_key = (ts // interval_sec) * interval_sec
        buckets.setdefault(bucket_key, []).append(dp.get("value", 0))
    result = []
    for ts in sorted(buckets):
        vals = buckets[ts]
        if aggregation == "avg":
            agg_val = round(sum(vals) / len(vals), 3)
        elif aggregation == "sum":
            agg_val = round(sum(vals), 3)
        elif aggregation == "min":
            agg_val = min(vals)
        elif aggregation == "max":
            agg_val = max(vals)
        elif aggregation == "count":
            agg_val = len(vals)
        elif aggregation == "p95":
            sorted_vals = sorted(vals)
            idx = min(int(math.ceil(len(sorted_vals) * 0.95)) - 1, len(sorted_vals) - 1)
            agg_val = sorted_vals[max(idx, 0)]
        else:
            agg_val = 0
        result.append({"timestamp": ts, "value": agg_val, "count": len(vals)})
    return {"buckets": result, "total_points": len(data_points),
            "bucket_count": len(result), "aggregation": aggregation}
