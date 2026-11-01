"""Fleet AI Platform Dashboard v3 — track unified AI platform control panel."""
from __future__ import annotations
def fleet_ai_platform_dashboard_v3(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    widgets = sum(d.get("widgets", 0) for d in dashboards)
    users_24h = sum(d.get("users_24h", 0) for d in dashboards)
    real_time = all(d.get("real_time", False) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "widgets": widgets,
            "users_24h": users_24h, "real_time": real_time, "live": real_time}
