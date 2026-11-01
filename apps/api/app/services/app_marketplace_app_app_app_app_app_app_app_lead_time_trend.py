"""Lead time trend — track lead time for changes (DORA metric)."""
from __future__ import annotations
def lead_time_trend(periods: list[dict]) -> dict:
    if len(periods) < 2: return {"trend": "stable"}
    times = [p.get("lead_time_hours", 0) for p in periods]
    recent = sum(times[-2:]) / 2
    older = sum(times[:2]) / 2
    trend = "improving" if recent < older * 0.8 else ("worsening" if recent > older * 1.2 else "stable")
    return {"trend": trend, "recent_avg": round(recent, 1), "older_avg": round(older, 1)}
