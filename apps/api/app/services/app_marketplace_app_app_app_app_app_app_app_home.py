"""App home — the complete app home page with all sections."""

import html
from datetime import datetime, timezone


def build_app_home(*, app: dict, stats: dict, recent_activity: list[dict],
                     has_update: bool = False) -> dict:
    return {
        "header": {
            "name": html.escape(app.get("name", "")),
            "icon": app.get("icon", "📦"),
            "version": app.get("version", "1.0.0"),
            "status": app.get("status", "active"),
            "published": app.get("published", False),
        },
        "quick_stats": [
            {"label": "Installs", "value": stats.get("installs", 0), "icon": "📥",
             "display": f"{stats.get('installs', 0):,}"},
            {"label": "API Calls", "value": stats.get("api_calls", 0), "icon": "🔗",
             "display": f"{stats.get('api_calls', 0):,}"},
            {"label": "Rating", "value": stats.get("rating", 0), "icon": "⭐",
             "display": f"{stats.get('rating', 0):.1f}/5"},
            {"label": "Reviews", "value": stats.get("reviews", 0), "icon": "💬"},
        ],
        "recent_activity": [{"action": html.escape(a.get("action", "")),
                              "timestamp": a.get("timestamp", "")}
                             for a in recent_activity[:5]],
        "has_update": has_update,
        "quick_links": [
            {"label": "Analytics", "href": "analytics", "icon": "📊"},
            {"label": "Webhooks", "href": "webhooks", "icon": "🔗"},
            {"label": "Settings", "href": "settings", "icon": "⚙️"},
            {"label": "Publish", "href": "publish", "icon": "🚀"},
        ],
    }
