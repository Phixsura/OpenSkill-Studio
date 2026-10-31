"""MTTR trend — track mean time to recovery over time."""
from __future__ import annotations
def mttr_trend(periods: list[dict]) -> dict:
    if len(periods) < 2: return {"trend": "stable"}
    mttrs = [p.get("mttr_min", 0) for p in periods]
    recent = sum(mttrs[-2:]) / 2
    older = sum(mttrs[:2]) / 2
    trend = "improving" if recent < older * 0.8 else ("worsening" if recent > older * 1.2 else "stable")
    return {"trend": trend, "recent_avg": round(recent, 1), "older_avg": round(older, 1)}
