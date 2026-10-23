"""Incident timeline — track and display platform incidents."""

from datetime import datetime, timedelta


def build_incident_timeline(*, days: int = 90) -> dict:
    base = datetime(2026, 10, 23)
    incidents = [
        {"id": "inc-001", "title": "API latency spike", "severity": "minor",
         "started": (base - timedelta(days=5)).isoformat(),
         "resolved": (base - timedelta(days=5, hours=-2)).isoformat(),
         "duration_min": 120, "affected": ["API", "Webhooks"]},
        {"id": "inc-002", "title": "Search index degraded", "severity": "major",
         "started": (base - timedelta(days=30)).isoformat(),
         "resolved": (base - timedelta(days=30, hours=-4)).isoformat(),
         "duration_min": 240, "affected": ["Search"]},
        {"id": "inc-003", "title": "CDN partial outage", "severity": "critical",
         "started": (base - timedelta(days=60)).isoformat(),
         "resolved": (base - timedelta(days=60, hours=-1)).isoformat(),
         "duration_min": 60, "affected": ["CDN", "Static Assets"]},
    ]
    total_min = sum(i["duration_min"] for i in incidents)
    uptime = round((1 - total_min / (days * 24 * 60)) * 100, 3)
    return {
        "period_days": days,
        "incidents": incidents,
        "total_incidents": len(incidents),
        "uptime_pct": uptime,
        "mttr_min": round(total_min / len(incidents), 1),
    }
