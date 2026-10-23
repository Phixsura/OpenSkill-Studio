"""App monitoring page — complete app monitoring dashboard."""

import html
from datetime import datetime, timezone


def build_monitoring_page(*, app_name: str, uptime_pct: float, avg_latency_ms: int,
                             error_rate_pct: float, active_users: int,
                             alerts: list[dict] | None = None) -> dict:
    health = "healthy" if error_rate_pct < 1 and avg_latency_ms < 200 else \
             "degraded" if error_rate_pct < 5 else "critical"
    return {
        "app_name": html.escape(app_name),
        "health": health,
        "health_icon": {"healthy": "🟢", "degraded": "🟡", "critical": "🔴"}.get(health, "⚪"),
        "metrics": [
            {"label": "Uptime", "value": uptime_pct, "display": f"{uptime_pct}%", "icon": "⬆️"},
            {"label": "Latency", "value": avg_latency_ms, "display": f"{avg_latency_ms}ms", "icon": "⚡"},
            {"label": "Error Rate", "value": error_rate_pct, "display": f"{error_rate_pct}%", "icon": "❌"},
            {"label": "Active Users", "value": active_users, "display": f"{active_users:,}", "icon": "👥"},
        ],
        "active_alerts": [{"title": html.escape(a.get("title", "")),
                            "severity": a.get("severity", "warning")}
                           for a in (alerts or [])],
        "alert_count": len(alerts or []),
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }
