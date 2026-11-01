"""Deployment count trend — track deployment frequency over time."""
from __future__ import annotations
def deploy_count_trend(periods: list[dict]) -> dict:
    if len(periods) < 2: return {"trend": "stable"}
    counts = [p.get("deploys", 0) for p in periods]
    recent = sum(counts[-2:]) / 2
    older = sum(counts[:2]) / 2
    trend = "accelerating" if recent > older * 1.2 else ("slowing" if recent < older * 0.8 else "steady")
    return {"trend": trend, "recent_avg": round(recent, 1), "older_avg": round(older, 1)}
