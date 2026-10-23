"""App dashboard — unified developer dashboard content builder."""

import html
from datetime import datetime, timezone


def build_dashboard(*, user_name: str, apps: list[dict], notifications: int = 0,
                      recent_deploys: int = 0, open_tickets: int = 0) -> dict:
    greeting = _get_greeting()
    app_summaries = []
    for a in apps[:5]:
        app_summaries.append({
            "id": a.get("id", ""),
            "name": html.escape(a.get("name", "")),
            "icon": a.get("icon", "📦"),
            "status": a.get("status", "active"),
            "downloads": a.get("downloads", 0),
        })
    return {
        "greeting": f"{greeting}, {html.escape(user_name)}!",
        "quick_stats": [
            {"label": "Your Apps", "value": len(apps), "icon": "📦"},
            {"label": "Notifications", "value": notifications, "icon": "🔔"},
            {"label": "Recent Deploys", "value": recent_deploys, "icon": "🚀"},
            {"label": "Open Tickets", "value": open_tickets, "icon": "🎫"},
        ],
        "recent_apps": app_summaries,
        "has_apps": len(apps) > 0,
    }


def _get_greeting() -> str:
    hour = datetime.now(timezone.utc).hour
    if hour < 12:
        return "Good morning"
    elif hour < 18:
        return "Good afternoon"
    return "Good evening"
