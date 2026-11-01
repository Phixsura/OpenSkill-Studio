"""Fleet AI Usage Analytics — track AI platform usage patterns."""
from __future__ import annotations
def fleet_ai_usage_analytics(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    users_dau = sum(d.get("dau", 0) for d in dashboards)
    requests_24h = sum(d.get("requests_24h", 0) for d in dashboards)
    retention_pct = round(sum(d.get("retention_pct", 0) for d in dashboards) / max(len(dashboards), 1), 1)
    return {"dashboards": len(dashboards), "active": len(active), "dau": users_dau,
            "requests_24h": requests_24h, "retention": retention_pct, "growing": retention_pct > 70}
