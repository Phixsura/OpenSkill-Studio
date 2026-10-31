"""Fleet AI User Analytics v2 — track platform user behavior analytics."""
from __future__ import annotations
def fleet_ai_user_analytics_v2(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    dau = sum(d.get("dau", 0) for d in dashboards)
    mau = sum(d.get("mau", 0) for d in dashboards)
    retention = round(sum(d.get("retention_pct", 0) for d in dashboards) / max(len(dashboards), 1), 1)
    engagement = round(sum(d.get("engagement_min", 0) for d in dashboards) / max(len(dashboards), 1), 1)
    return {"dashboards": len(dashboards), "active": len(active), "dau": dau,
            "mau": mau, "retention": retention, "engagement_min": engagement, "growing": retention > 70}
