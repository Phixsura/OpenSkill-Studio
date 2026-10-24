"""Status indicator — map system states to visual indicators."""
from __future__ import annotations

STATUS_MAP = {
    "operational": {"color": "green", "icon": "🟢", "label": "Operational"},
    "degraded": {"color": "yellow", "icon": "🟡", "label": "Degraded Performance"},
    "partial_outage": {"color": "orange", "icon": "🟠", "label": "Partial Outage"},
    "major_outage": {"color": "red", "icon": "🔴", "label": "Major Outage"},
    "maintenance": {"color": "blue", "icon": "🔵", "label": "Under Maintenance"},
    "unknown": {"color": "gray", "icon": "⚪", "label": "Unknown"},
}


def get_indicator(status: str) -> dict:
    info = STATUS_MAP.get(status, STATUS_MAP["unknown"])
    return {"status": status, **info}


def aggregate_status(services: list[dict]) -> dict:
    statuses = [s.get("status", "unknown") for s in services]
    if "major_outage" in statuses:
        overall = "major_outage"
    elif "partial_outage" in statuses:
        overall = "partial_outage"
    elif "degraded" in statuses:
        overall = "degraded"
    elif "maintenance" in statuses:
        overall = "maintenance"
    elif all(s == "operational" for s in statuses):
        overall = "operational"
    else:
        overall = "unknown"
    return {"overall": get_indicator(overall),
            "services": [{"name": s.get("name", ""), **get_indicator(s.get("status", "unknown"))}
                          for s in services],
            "operational_count": statuses.count("operational"),
            "total": len(statuses)}
