"""Incident postmortem generator — structured postmortem from incident data."""
from __future__ import annotations


def generate_postmortem(incident: dict) -> dict:
    duration_min = round((incident.get("resolved_at", 0) - incident.get("detected_at", 0)) / 60, 1)
    impact_users = incident.get("affected_users", 0)
    severity = incident.get("severity", "medium")
    timeline = incident.get("timeline", [])
    root_cause = incident.get("root_cause", "Under investigation")
    action_items = incident.get("action_items", [])
    return {"title": incident.get("title", "Incident"),
            "severity": severity, "duration_minutes": duration_min,
            "impact": {"users_affected": impact_users,
                       "services_affected": incident.get("services", [])},
            "timeline": timeline, "root_cause": root_cause,
            "action_items": action_items,
            "lessons_learned": incident.get("lessons", []),
            "status": "completed" if action_items else "draft"}


def incident_stats(incidents: list[dict]) -> dict:
    total = len(incidents)
    by_severity: dict[str, int] = {}
    total_duration = 0
    for inc in incidents:
        sev = inc.get("severity", "medium")
        by_severity[sev] = by_severity.get(sev, 0) + 1
        total_duration += inc.get("duration_minutes", 0)
    avg_duration = round(total_duration / max(total, 1), 1)
    return {"total": total, "by_severity": by_severity,
            "avg_duration_minutes": avg_duration}
