"""Incident timeline — track incident lifecycle events."""
from __future__ import annotations

SEVERITIES = {"critical": 1, "major": 2, "minor": 3, "info": 4}


def build_incident(title: str, severity: str, events: list[dict]) -> dict:
    status = "open"
    for e in events:
        if e.get("type") == "resolved":
            status = "resolved"
        elif e.get("type") == "acknowledged":
            status = "acknowledged"
    duration_min = 0
    if len(events) >= 2:
        first_ts = events[0].get("timestamp", 0)
        last_ts = events[-1].get("timestamp", 0)
        duration_min = round((last_ts - first_ts) / 60)
    return {"title": title, "severity": severity,
            "severity_level": SEVERITIES.get(severity, 4),
            "status": status, "events": events, "event_count": len(events),
            "duration_min": duration_min}


def summarize_incidents(incidents: list[dict]) -> dict:
    by_sev = {}
    open_count = 0
    for inc in incidents:
        sev = inc.get("severity", "info")
        by_sev[sev] = by_sev.get(sev, 0) + 1
        if inc.get("status") != "resolved":
            open_count += 1
    return {"total": len(incidents), "open": open_count,
            "resolved": len(incidents) - open_count, "by_severity": by_sev}
