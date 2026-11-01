"""Incident response — manage incident lifecycle and communication."""

import secrets
from datetime import datetime


SEVERITY_MAP = {"sev1": "Critical", "sev2": "Major", "sev3": "Minor", "sev4": "Low"}


def create_incident(*, title: str, severity: str, reported_by: str,
                       affected_services: list[str]) -> dict:
    if severity not in SEVERITY_MAP:
        return {"error": f"Invalid severity. Valid: {', '.join(sorted(SEVERITY_MAP))}"}
    return {
        "incident_id": f"INC-{secrets.token_hex(4).upper()}",
        "title": title,
        "severity": severity,
        "severity_label": SEVERITY_MAP[severity],
        "reported_by": reported_by,
        "affected_services": affected_services,
        "status": "investigating",
        "timeline": [{"action": "created", "by": reported_by,
                       "at": datetime.utcnow().isoformat()}],
        "created_at": datetime.utcnow().isoformat(),
    }


def add_update(*, incident: dict, message: str, status: str, by: str) -> dict:
    valid_statuses = {"investigating", "identified", "monitoring", "resolved"}
    if status not in valid_statuses:
        return {"error": f"Invalid status. Valid: {', '.join(sorted(valid_statuses))}"}
    timeline = incident.get("timeline", [])
    timeline.append({"action": status, "message": message, "by": by,
                      "at": datetime.utcnow().isoformat()})
    return {**incident, "status": status, "timeline": timeline,
            "resolved_at": datetime.utcnow().isoformat() if status == "resolved" else None}
