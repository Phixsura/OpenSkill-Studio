"""Status indicator — real-time status indicators for dashboard widgets."""


STATUS_CONFIGS = {
    "operational": {"label": "Operational", "color": "green", "icon": "🟢", "priority": 0},
    "degraded": {"label": "Degraded Performance", "color": "yellow", "icon": "🟡", "priority": 1},
    "partial_outage": {"label": "Partial Outage", "color": "orange", "icon": "🟠", "priority": 2},
    "major_outage": {"label": "Major Outage", "color": "red", "icon": "🔴", "priority": 3},
    "maintenance": {"label": "Under Maintenance", "color": "blue", "icon": "🔵", "priority": 1},
}


def get_status_indicator(*, status: str) -> dict:
    config = STATUS_CONFIGS.get(status, STATUS_CONFIGS["operational"])
    return {"status": status, **config}


def get_aggregate_status(*, components: list[dict]) -> dict:
    if not components:
        return {"status": "unknown", "label": "No Data", "icon": "⚪"}
    worst = max(components, key=lambda c: STATUS_CONFIGS.get(c.get("status", "operational"), {}).get("priority", 0))
    worst_status = worst.get("status", "operational")
    config = STATUS_CONFIGS.get(worst_status, STATUS_CONFIGS["operational"])
    healthy = sum(1 for c in components if c.get("status") == "operational")
    return {
        "status": worst_status,
        **config,
        "healthy_count": healthy,
        "total_count": len(components),
        "all_operational": healthy == len(components),
    }
