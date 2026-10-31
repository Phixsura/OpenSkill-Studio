"""Incident tracker — incident lifecycle management."""

import html
import secrets
from datetime import datetime, timezone

SEVERITIES = {"sev1": "Critical", "sev2": "Major", "sev3": "Minor", "sev4": "Low"}
STATUSES = ["investigating", "identified", "monitoring", "resolved"]


def create_incident(*, title: str, severity: str = "sev3",
                      description: str = "") -> dict:
    iid = f"INC-{secrets.token_hex(4).upper()}"
    return {"id": iid, "title": html.escape(title),
            "description": html.escape(description),
            "severity": severity, "severity_label": SEVERITIES.get(severity, "Unknown"),
            "status": "investigating",
            "created_at": datetime.now(timezone.utc).isoformat(),
            "timeline": [{"status": "investigating",
                           "timestamp": datetime.now(timezone.utc).isoformat(),
                           "message": "Incident created"}]}


def update_status(*, incident: dict, status: str, message: str = "") -> dict:
    if status not in STATUSES:
        return {"error": f"Invalid status. Must be one of: {', '.join(STATUSES)}"}
    incident["status"] = status
    incident["timeline"].append({
        "status": status, "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": html.escape(message)})
    if status == "resolved":
        incident["resolved_at"] = datetime.now(timezone.utc).isoformat()
    return incident


def build_incident_dashboard(*, incidents: list[dict]) -> dict:
    active = [i for i in incidents if i.get("status") != "resolved"]
    by_severity = {}
    for i in active:
        s = i.get("severity", "sev4")
        by_severity[s] = by_severity.get(s, 0) + 1
    return {"active": len(active), "resolved": len(incidents) - len(active),
            "total": len(incidents), "by_severity": by_severity,
            "has_critical": by_severity.get("sev1", 0) > 0}
