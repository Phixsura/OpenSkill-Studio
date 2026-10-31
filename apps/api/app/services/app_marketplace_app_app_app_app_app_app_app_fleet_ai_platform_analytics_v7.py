"""Fleet AI Analytics v7 — track comprehensive platform analytics."""
from __future__ import annotations
def fleet_ai_analytics_v7(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    events_24h = sum(d.get("events", 0) for d in dashboards)
    insights = sum(d.get("insights", 0) for d in dashboards)
    reports = sum(d.get("reports", 0) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "events": events_24h,
            "insights": insights, "reports": reports, "data_driven": insights > 0}
