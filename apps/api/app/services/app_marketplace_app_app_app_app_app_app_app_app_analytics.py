"""App analytics summary — per-app usage metrics for developer dashboards."""
from __future__ import annotations


def compute_app_analytics(*, app_id: str, installs: int, uninstalls: int,
                             api_calls: int, active_users: int,
                             errors: int, avg_response_ms: float,
                             rating: float, reviews: int) -> dict:
    net_installs = installs - uninstalls
    error_rate = round(errors / max(api_calls, 1) * 100, 2)
    retention = round(active_users / max(installs, 1) * 100, 1) if installs else 0
    health = "excellent" if error_rate < 0.5 and avg_response_ms < 200 else \
             "good" if error_rate < 2 and avg_response_ms < 500 else \
             "needs_attention" if error_rate < 5 else "critical"
    return {
        "app_id": app_id,
        "installs": installs, "uninstalls": uninstalls,
        "net_installs": net_installs, "net_display": f"+{net_installs}" if net_installs > 0 else str(net_installs),
        "api_calls": api_calls, "api_display": f"{api_calls:,}",
        "active_users": active_users, "retention_pct": retention,
        "errors": errors, "error_rate": error_rate,
        "avg_response_ms": avg_response_ms,
        "rating": rating, "reviews": reviews,
        "health": health,
    }
