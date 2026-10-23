"""Platform status summary — the final aggregated platform status page."""

from datetime import datetime


def build_status_summary(*, services: list[dict], active_incidents: int,
                            uptime_90d: float, last_incident_days_ago: int) -> dict:
    operational = sum(1 for s in services if s.get("status") == "operational")
    degraded = sum(1 for s in services if s.get("status") == "degraded")
    down = sum(1 for s in services if s.get("status") == "outage")

    if down > 0:
        overall = "major_outage"
    elif degraded > 0:
        overall = "partial_outage"
    elif active_incidents > 0:
        overall = "investigating"
    else:
        overall = "all_operational"

    return {
        "overall_status": overall,
        "services": services,
        "service_count": len(services),
        "operational": operational,
        "degraded": degraded,
        "down": down,
        "active_incidents": active_incidents,
        "uptime_90d": uptime_90d,
        "last_incident_days_ago": last_incident_days_ago,
        "updated_at": datetime.utcnow().isoformat(),
    }
