"""Platform dashboard summary — unified overview of the entire developer platform."""
from __future__ import annotations


def build_dashboard_summary(*, apps: int = 0, developers: int = 0,
                              api_calls_24h: int = 0, uptime_pct: float = 99.9,
                              revenue_mrr: float = 0, active_webhooks: int = 0,
                              error_rate_pct: float = 0, avg_latency_ms: float = 0,
                              deployments_today: int = 0, open_incidents: int = 0) -> dict:
    health_score = 100
    if uptime_pct < 99.5:
        health_score -= 30
    if error_rate_pct > 1:
        health_score -= 20
    if avg_latency_ms > 500:
        health_score -= 15
    if open_incidents > 0:
        health_score -= min(open_incidents * 10, 35)
    health_score = max(0, health_score)
    status = "excellent" if health_score >= 90 else "good" if health_score >= 70 else \
             "fair" if health_score >= 50 else "poor"
    return {
        "health_score": health_score, "health_display": f"{health_score}/100",
        "status": status,
        "metrics": {
            "apps": {"value": apps, "display": f"{apps:,}"},
            "developers": {"value": developers, "display": f"{developers:,}"},
            "api_calls_24h": {"value": api_calls_24h, "display": f"{api_calls_24h:,}"},
            "uptime": {"value": uptime_pct, "display": f"{uptime_pct}%"},
            "mrr": {"value": revenue_mrr, "display": f"${revenue_mrr:,.0f}"},
            "webhooks": {"value": active_webhooks, "display": f"{active_webhooks:,}"},
            "error_rate": {"value": error_rate_pct, "display": f"{error_rate_pct}%"},
            "latency": {"value": avg_latency_ms, "display": f"{avg_latency_ms:.0f}ms"},
            "deploys_today": {"value": deployments_today, "display": str(deployments_today)},
            "incidents": {"value": open_incidents, "display": str(open_incidents)},
        },
        "milestone": "🏆 2,100 COMMITS — OpenSkill Developer Platform",
    }
