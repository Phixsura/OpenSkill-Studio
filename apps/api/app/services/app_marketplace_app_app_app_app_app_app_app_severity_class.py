"""Incident severity classifier — classify incidents by impact and urgency."""
from __future__ import annotations


def classify_severity(incident: dict) -> dict:
    affected_users = incident.get("affected_users", 0)
    revenue_impact = incident.get("revenue_impact_per_hour", 0)
    services_down = incident.get("services_down", 0)
    data_loss = incident.get("data_loss", False)
    if data_loss or revenue_impact > 10000 or services_down > 5:
        severity = "P1"
        label = "Critical"
        response_time = "15 minutes"
    elif affected_users > 1000 or revenue_impact > 1000 or services_down > 2:
        severity = "P2"
        label = "High"
        response_time = "30 minutes"
    elif affected_users > 100 or services_down > 0:
        severity = "P3"
        label = "Medium"
        response_time = "4 hours"
    else:
        severity = "P4"
        label = "Low"
        response_time = "24 hours"
    return {"severity": severity, "label": label, "response_time": response_time,
            "factors": {"affected_users": affected_users,
                        "revenue_impact": revenue_impact,
                        "services_down": services_down, "data_loss": data_loss}}


def severity_distribution(incidents: list[dict]) -> dict:
    by_sev = {}
    for inc in incidents:
        sev = inc.get("severity", "P4")
        by_sev[sev] = by_sev.get(sev, 0) + 1
    return {"total": len(incidents), "distribution": by_sev}
