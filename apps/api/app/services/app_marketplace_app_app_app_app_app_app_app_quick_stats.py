"""Platform quick stats — lightweight summary for dashboard header."""
from __future__ import annotations


def compute_quick_stats(*, total_apps: int, total_developers: int,
                          api_calls_today: int, active_deployments: int,
                          open_incidents: int, uptime_pct: float) -> dict:
    health = "🟢" if uptime_pct >= 99.9 and open_incidents == 0 else \
             "🟡" if uptime_pct >= 99 else "🔴"
    return {
        "stats": [
            {"label": "Apps", "value": total_apps, "display": f"{total_apps:,}", "icon": "📱"},
            {"label": "Developers", "value": total_developers, "display": f"{total_developers:,}", "icon": "👩‍💻"},
            {"label": "API Calls", "value": api_calls_today, "display": f"{api_calls_today:,}", "icon": "📡"},
            {"label": "Deployments", "value": active_deployments, "display": str(active_deployments), "icon": "🚀"},
            {"label": "Incidents", "value": open_incidents, "display": str(open_incidents), "icon": "🚨"},
            {"label": "Uptime", "value": uptime_pct, "display": f"{uptime_pct}%", "icon": health},
        ],
    }
