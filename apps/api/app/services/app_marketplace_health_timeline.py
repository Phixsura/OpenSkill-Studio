"""Health timeline — historical health status over time."""

from datetime import datetime, timezone


def build_health_timeline(*, checks: list[dict], period_days: int = 30) -> dict:
    timeline = []
    for check in checks[-period_days * 24:]:  # hourly checks
        timeline.append({
            "timestamp": check.get("timestamp", ""),
            "status": check.get("status", "unknown"),
            "response_ms": check.get("response_ms", 0),
        })
    statuses = [t["status"] for t in timeline]
    healthy_count = statuses.count("healthy")
    total = len(statuses) or 1
    return {
        "timeline": timeline[-168:],  # last 7 days hourly
        "period_days": period_days,
        "uptime_pct": round(healthy_count / total * 100, 3),
        "total_checks": len(timeline),
        "current_status": statuses[-1] if statuses else "unknown",
    }


def get_downtime_incidents(*, timeline: list[dict]) -> list[dict]:
    incidents = []
    in_incident = False
    start = None
    for t in timeline:
        if t["status"] != "healthy" and not in_incident:
            in_incident = True
            start = t["timestamp"]
        elif t["status"] == "healthy" and in_incident:
            in_incident = False
            incidents.append({"start": start, "end": t["timestamp"], "resolved": True})
    if in_incident:
        incidents.append({"start": start, "end": None, "resolved": False})
    return incidents


def compute_mtbf(*, incidents: list[dict], total_hours: int) -> dict:
    if not incidents:
        return {"mtbf_hours": total_hours, "incident_count": 0}
    mtbf = total_hours / len(incidents)
    return {"mtbf_hours": round(mtbf, 1), "incident_count": len(incidents)}
