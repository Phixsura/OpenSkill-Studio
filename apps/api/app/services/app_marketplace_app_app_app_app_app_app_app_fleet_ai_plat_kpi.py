"""Fleet AI Platform KPI — track key performance indicators dashboard."""
from __future__ import annotations
def fleet_ai_platform_kpi(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    kpis = sum(d.get("kpis", 0) for d in dashboards)
    green = sum(d.get("green", 0) for d in dashboards)
    red = sum(d.get("red", 0) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "kpis": kpis,
            "green": green, "red": red, "on_track": red == 0}
