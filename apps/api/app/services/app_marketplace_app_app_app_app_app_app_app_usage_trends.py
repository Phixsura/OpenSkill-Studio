"""API usage trends — analyze usage patterns over time."""
from __future__ import annotations
import math


def compute_trends(data_points: list[dict]) -> dict:
    if len(data_points) < 2:
        return {"trend": "insufficient_data", "data_points": len(data_points)}
    values = [d.get("value", 0) for d in data_points]
    first_half = values[:len(values)//2]
    second_half = values[len(values)//2:]
    avg_first = sum(first_half) / len(first_half)
    avg_second = sum(second_half) / len(second_half)
    change = round((avg_second - avg_first) / max(avg_first, 1) * 100, 1)
    peak = max(values)
    trough = min(values)
    avg = round(sum(values) / len(values), 1)
    trend = "growing" if change > 10 else "declining" if change < -10 else "stable"
    return {
        "trend": trend, "change_pct": change,
        "avg": avg, "peak": peak, "trough": trough,
        "data_points": len(values),
        "volatility": round((peak - trough) / max(avg, 1) * 100, 1),
    }
