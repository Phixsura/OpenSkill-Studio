"""Incident report — track and communicate app outages."""

from datetime import datetime, timezone

SEVERITIES = {"minor", "major", "critical"}
STATUSES = {"investigating", "identified", "monitoring", "resolved"}


def create_incident(*, app_id: str, title: str, severity: str, description: str) -> dict:
    if severity not in SEVERITIES:
        return {"error": f"Invalid severity. Use: {', '.join(sorted(SEVERITIES))}"}
    return {
        "app_id": app_id, "title": title, "severity": severity, "description": description,
        "status": "investigating", "updates": [], "error": None,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def add_update(*, incident: dict, message: str, new_status: str) -> dict:
    if new_status not in STATUSES:
        return {"error": f"Invalid status: {new_status}"}
    updates = list(incident.get("updates", []))
    updates.append({"message": message, "status": new_status, "timestamp": datetime.now(timezone.utc).isoformat()})
    return {**incident, "status": new_status, "updates": updates, "error": None}


def compute_uptime(*, incidents: list[dict], period_hours: int = 720) -> dict:
    total_downtime_hours = sum(i.get("downtime_hours", 0) for i in incidents)
    uptime_pct = round((period_hours - total_downtime_hours) / period_hours * 100, 3)
    return {"uptime_pct": uptime_pct, "incidents": len(incidents), "period_hours": period_hours}
