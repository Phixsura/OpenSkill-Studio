"""App analytics overview — dashboard metrics for app publishers."""

import html
from datetime import datetime, timezone


def build_analytics_overview(*, app_id: str, period: str = "30d",
                                installs: int, uninstalls: int,
                                active_users: int, api_calls: int,
                                avg_rating: float, reviews: int) -> dict:
    net_installs = installs - uninstalls
    retention = round(active_users / max(installs, 1) * 100, 1) if installs else 0
    return {
        "app_id": app_id, "period": period,
        "metrics": [
            {"label": "Installs", "value": installs, "icon": "📥", "trend": "up" if net_installs > 0 else "down"},
            {"label": "Active Users", "value": active_users, "icon": "👥"},
            {"label": "API Calls", "value": api_calls, "icon": "🔗",
             "display": f"{api_calls/1000:.1f}K" if api_calls >= 1000 else str(api_calls)},
            {"label": "Avg Rating", "value": avg_rating, "icon": "⭐",
             "display": f"{avg_rating:.1f}/5"},
            {"label": "Reviews", "value": reviews, "icon": "💬"},
            {"label": "Retention", "value": retention, "icon": "🔄",
             "display": f"{retention}%"},
        ],
        "net_installs": net_installs,
        "health": "good" if avg_rating >= 4 and retention >= 50 else "needs_attention",
    }
