"""Fleet Grafana — track dashboard coverage and usage."""
from __future__ import annotations
def fleet_grafana_dashboards(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("views_7d", 0) > 0]
    stale = [d for d in dashboards if d.get("views_7d", 0) == 0 and d.get("age_days", 0) > 90]
    return {"total": len(dashboards), "active": len(active), "stale": len(stale),
            "usage_rate": round(len(active) / max(len(dashboards), 1) * 100, 1)}
