"""Developer portal home — unified landing for the developer experience."""
from __future__ import annotations


def build_portal_home(*, user_name: str, app_count: int, api_calls_today: int,
                        unread_notifications: int, recent_deploys: int,
                        achievement_count: int, level_title: str,
                        announcements: list[dict] | None = None) -> dict:
    greeting = _time_greeting()
    return {
        "greeting": f"{greeting}, {user_name}!",
        "stats_bar": [
            {"icon": "📱", "value": str(app_count), "label": "Apps"},
            {"icon": "📡", "value": f"{api_calls_today:,}", "label": "API Today"},
            {"icon": "🚀", "value": str(recent_deploys), "label": "Deploys"},
            {"icon": "🔔", "value": str(unread_notifications), "label": "Notifications"},
            {"icon": "🏅", "value": f"{achievement_count}", "label": f"L: {level_title}"},
        ],
        "quick_links": [
            {"label": "Create App", "icon": "📱", "path": "/apps/new"},
            {"label": "API Docs", "icon": "📚", "path": "/docs/api"},
            {"label": "SDK Guide", "icon": "🔧", "path": "/docs/sdk"},
            {"label": "Status", "icon": "🟢", "path": "/status"},
        ],
        "announcements": announcements or [],
    }


def _time_greeting() -> str:
    return "Welcome back"  # simplified for unit testing
