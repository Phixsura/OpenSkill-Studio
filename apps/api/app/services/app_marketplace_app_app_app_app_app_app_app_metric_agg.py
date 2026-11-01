"""Metric aggregation engine — aggregate metrics across time windows."""
from __future__ import annotations


def aggregate_metrics(data_points: list[float], window: str = "1h") -> dict:
    if not data_points:
        return {"count": 0, "sum": 0, "avg": 0, "min": 0, "max": 0, "window": window}
    s = sorted(data_points)
    return {"count": len(s), "sum": round(sum(s), 2),
            "avg": round(sum(s) / len(s), 2), "min": s[0], "max": s[-1],
            "p50": s[len(s) // 2], "p95": s[int(len(s) * 0.95)],
            "p99": s[int(min(len(s) * 0.99, len(s) - 1))],
            "window": window}


def downsample(points: list[dict], factor: int = 10) -> list[dict]:
    result = []
    for i in range(0, len(points), factor):
        batch = points[i:i + factor]
        values = [p.get("value", 0) for p in batch]
        result.append({"timestamp": batch[0].get("timestamp", 0),
                        "avg": round(sum(values) / len(values), 2),
                        "min": min(values), "max": max(values),
                        "count": len(values)})
    return result
