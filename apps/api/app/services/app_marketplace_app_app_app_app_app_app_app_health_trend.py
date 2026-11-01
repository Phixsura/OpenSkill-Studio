"""Service health trend analyzer — analyze health trends over time."""
from __future__ import annotations


def analyze_trend(snapshots: list[dict]) -> dict:
    if len(snapshots) < 2:
        return {"trend": "insufficient_data", "data_points": len(snapshots)}
    uptimes = [s.get("uptime_pct", 100) for s in snapshots]
    avg = round(sum(uptimes) / len(uptimes), 2)
    n = len(uptimes)
    half = n // 2
    recent_avg = round(sum(uptimes[half:]) / max(n - half, 1), 2)
    older_avg = round(sum(uptimes[:half]) / max(half, 1), 2)
    if recent_avg > older_avg + 0.5:
        trend = "improving"
    elif recent_avg < older_avg - 0.5:
        trend = "degrading"
    else:
        trend = "stable"
    return {"trend": trend, "avg_uptime": avg, "recent_avg": recent_avg,
            "worst": min(uptimes), "best": max(uptimes), "data_points": n}


def predict_sla(trend_data: dict, sla_target: float = 99.9) -> dict:
    avg = trend_data.get("avg_uptime", 100)
    on_track = avg >= sla_target
    gap = round(avg - sla_target, 3)
    return {"on_track": on_track, "current_avg": avg, "sla_target": sla_target,
            "gap": gap, "risk": "low" if gap > 0 else ("medium" if gap > -0.5 else "high")}
