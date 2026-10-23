"""Developer status dashboard — real-time platform status for developers."""


def build_developer_status_dashboard(*, services: list[dict], scheduled_maintenance: list[dict],
                                         recent_incidents: list[dict], uptime_90d: float) -> dict:
    all_operational = all(s.get("status") == "operational" for s in services)
    active_maintenance = [m for m in scheduled_maintenance if m.get("status") == "scheduled"]
    active_incidents = [i for i in recent_incidents if i.get("status") != "resolved"]
    overall = "operational" if all_operational and not active_incidents else \
              "major_outage" if any(s.get("status") == "major_outage" for s in services) else "partial_outage"
    return {
        "page_type": "developer_status",
        "overall_status": overall,
        "uptime_90d": uptime_90d,
        "services": services,
        "active_incidents": active_incidents,
        "scheduled_maintenance": active_maintenance,
        "subscribe_options": ["email", "slack", "rss", "webhook"],
        "status_page_url": "https://status.openskill.dev",
    }
