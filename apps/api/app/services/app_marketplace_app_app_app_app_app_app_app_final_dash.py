"""Final marketplace dashboard — unified view of the entire platform."""
from __future__ import annotations


def build_final_dashboard(*, total_apps: int, total_devs: int, total_installs: int,
                             total_api_calls: int, uptime_pct: float, avg_rating: float,
                             active_users: int, revenue_mrr: float,
                             open_incidents: int, pending_reviews: int) -> dict:
    health = 100
    if uptime_pct < 99.5:
        health -= 30
    if open_incidents > 0:
        health -= min(open_incidents * 10, 30)
    if avg_rating < 4.0:
        health -= 15
    health = max(0, health)
    status = "excellent" if health >= 90 else "good" if health >= 70 else "needs_attention"
    return {
        "health_score": health, "health_display": f"{health}/100", "status": status,
        "metrics": {
            "apps": {"value": total_apps, "display": f"{total_apps:,}"},
            "developers": {"value": total_devs, "display": f"{total_devs:,}"},
            "installs": {"value": total_installs, "display": f"{total_installs:,}"},
            "api_calls": {"value": total_api_calls, "display": f"{total_api_calls:,}"},
            "uptime": {"value": uptime_pct, "display": f"{uptime_pct}%"},
            "rating": {"value": avg_rating, "display": f"{avg_rating} ⭐"},
            "active_users": {"value": active_users, "display": f"{active_users:,}"},
            "mrr": {"value": revenue_mrr, "display": f"${revenue_mrr:,.0f}"},
        },
        "alerts": {
            "incidents": open_incidents,
            "pending_reviews": pending_reviews,
            "has_alerts": open_incidents > 0 or pending_reviews > 5,
        },
    }
