"""Incident page — public incident detail with timeline."""

import html
from datetime import datetime, timezone

STATUS_ICONS = {"investigating": "🔍", "identified": "🎯", "monitoring": "👁️", "resolved": "✅"}


def build_incident_page(*, incident: dict) -> dict:
    timeline = []
    for update in incident.get("updates", []):
        timeline.append({
            "status": update.get("status", "investigating"),
            "icon": STATUS_ICONS.get(update.get("status", ""), "📌"),
            "message": html.escape(update.get("message", "")),
            "timestamp": update.get("timestamp", ""),
        })
    return {
        "title": html.escape(incident.get("title", "")),
        "severity": incident.get("severity", "minor"),
        "status": incident.get("status", "investigating"),
        "status_icon": STATUS_ICONS.get(incident.get("status", ""), "🔍"),
        "affected_services": incident.get("affected_services", []),
        "timeline": timeline,
        "created_at": incident.get("created_at", ""),
        "resolved_at": incident.get("resolved_at"),
        "is_resolved": incident.get("status") == "resolved",
    }
