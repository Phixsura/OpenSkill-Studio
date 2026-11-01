"""Fleet AI API Analytics — track AI API usage patterns and insights."""
from __future__ import annotations
def fleet_ai_api_analytics(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    endpoints = sum(d.get("endpoints", 0) for d in dashboards)
    calls_24h = sum(d.get("calls_24h", 0) for d in dashboards)
    error_rate = round(sum(d.get("error_rate", 0) for d in dashboards) / max(len(dashboards), 1), 2)
    return {"dashboards": len(dashboards), "active": len(active), "endpoints": endpoints,
            "calls_24h": calls_24h, "error_rate": error_rate, "healthy": error_rate < 1}
