"""Fleet AI Dashboard v5 — track ultimate unified platform dashboard."""
from __future__ import annotations
def fleet_ai_dashboard_v5(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    widgets = sum(d.get("widgets", 0) for d in dashboards)
    users_24h = sum(d.get("users_24h", 0) for d in dashboards)
    custom_views = sum(d.get("custom_views", 0) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "widgets": widgets,
            "users_24h": users_24h, "custom_views": custom_views, "popular": users_24h > 1000}
