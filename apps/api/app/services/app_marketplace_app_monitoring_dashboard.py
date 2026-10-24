"""Monitoring dashboard — real-time metrics visualization for apps."""


def build_monitoring_dashboard(*, app: dict, metrics: dict, alerts: list[dict],
                                  uptime_history: list[dict]) -> dict:
    active_alerts = [a for a in alerts if a.get("triggered")]
    health = "critical" if len(active_alerts) >= 3 else "warning" if active_alerts else "healthy"
    return {
        "page_type": "monitoring",
        "app": {"id": app["id"], "name": app["name"]},
        "health": health,
        "panels": [
            {"key": "metrics", "title": "Real-time Metrics", "data": metrics},
            {"key": "alerts", "title": f"Alerts ({len(active_alerts)} active)", "data": alerts},
            {"key": "uptime", "title": "Uptime History", "data": uptime_history[:30]},
            {"key": "logs", "title": "Live Logs", "icon": "📋"},
        ],
    }
