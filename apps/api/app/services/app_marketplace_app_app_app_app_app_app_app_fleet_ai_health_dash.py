"""Fleet AI Health Dashboard — track unified AI platform health view."""
from __future__ import annotations
def fleet_ai_health_dashboard(dashboards: list[dict]) -> dict:
    active = [d for d in dashboards if d.get("active", True)]
    services_monitored = sum(d.get("services", 0) for d in dashboards)
    healthy = sum(d.get("healthy", 0) for d in dashboards)
    alerts_active = sum(d.get("alerts", 0) for d in dashboards)
    health_pct = round(healthy / max(services_monitored, 1) * 100, 1)
    return {"dashboards": len(dashboards), "active": len(active), "services": services_monitored,
            "healthy": healthy, "alerts": alerts_active, "health_pct": health_pct, "green": health_pct > 99}
