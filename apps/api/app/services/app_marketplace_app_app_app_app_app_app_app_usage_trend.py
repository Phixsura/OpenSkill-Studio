"""Usage trend analyzer — identify usage patterns and anomalies."""
from __future__ import annotations


def analyze_trend(data_points: list[float], window: int = 7) -> dict:
    if len(data_points) < window:
        return {"trend": "insufficient_data", "points": len(data_points)}
    recent = data_points[-window:]
    older = data_points[-2*window:-window] if len(data_points) >= 2*window else data_points[:len(data_points)-window]
    recent_avg = round(sum(recent) / len(recent), 2)
    older_avg = round(sum(older) / max(len(older), 1), 2)
    growth = round((recent_avg - older_avg) / max(abs(older_avg), 0.01) * 100, 1)
    trend = "growing" if growth > 5 else "declining" if growth < -5 else "stable"
    peak = max(data_points)
    trough = min(data_points)
    return {"trend": trend, "growth_pct": growth, "recent_avg": recent_avg,
            "older_avg": older_avg, "peak": peak, "trough": trough,
            "points": len(data_points)}
