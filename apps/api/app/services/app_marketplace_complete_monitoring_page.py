"""Complete monitoring page — real-time monitoring with alerts and dashboards."""


def build_complete_monitoring_page(*, app: dict, metrics: dict, alerts: list[dict],
                                       uptime: dict, error_budget: dict,
                                       health_checks: list[dict]) -> dict:
    active_alerts = [a for a in alerts if a.get("triggered")]
    failing_checks = [h for h in health_checks if h.get("status") != "pass"]
    return {
        "page_type": "monitoring_dashboard",
        "app": {"id": app["id"], "name": app["name"]},
        "health": "critical" if len(active_alerts) >= 3 else "warning" if active_alerts else "healthy",
        "panels": [
            {"key": "overview", "title": "Overview", "icon": "📊"},
            {"key": "metrics", "title": "Metrics", "icon": "📈", "data": metrics},
            {"key": "alerts", "title": f"Alerts ({len(active_alerts)} active)", "icon": "🔔"},
            {"key": "uptime", "title": "Uptime", "icon": "📊", "data": uptime},
            {"key": "budget", "title": "Error Budget", "icon": "💰", "data": error_budget},
            {"key": "checks", "title": f"Health ({len(failing_checks)} failing)", "icon": "🏥"},
        ],
    }
