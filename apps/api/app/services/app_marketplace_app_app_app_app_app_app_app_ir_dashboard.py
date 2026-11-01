"""Incident response dashboard — unified incident response view."""
from __future__ import annotations


def incident_response_dashboard(incidents: list[dict], on_call: dict) -> dict:
    active = [i for i in incidents if i.get("status") == "active"]
    investigating = [i for i in incidents if i.get("status") == "investigating"]
    resolved_today = [i for i in incidents if i.get("status") == "resolved" and i.get("today")]
    total_active = len(active) + len(investigating)
    severity_counts = {}
    for i in active + investigating:
        sev = i.get("severity", "P3")
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
    return {"active_count": total_active, "active": active,
            "investigating": investigating, "resolved_today": len(resolved_today),
            "severity_counts": severity_counts,
            "on_call": on_call, "escalation_needed": any(i.get("severity") == "P1" for i in active)}
