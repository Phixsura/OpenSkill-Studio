"""Fleet Evidently — track ML model monitoring."""
from __future__ import annotations
def fleet_evidently_status(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    reports_24h = sum(d.get("reports_24h", 0) for d in dashboards)
    drift_alerts = sum(d.get("drift_alerts", 0) for d in dashboards)
    return {"dashboards": len(dashboards), "active": len(active), "reports_24h": reports_24h,
            "drift_alerts": drift_alerts, "stable": drift_alerts == 0}
