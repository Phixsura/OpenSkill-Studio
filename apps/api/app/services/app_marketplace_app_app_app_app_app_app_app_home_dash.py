"""Marketplace home dashboard — the definitive home page data source."""
from __future__ import annotations


def build_home_dashboard(*, user: dict, apps: list[dict], notifications: int,
                            health_score: int, recent_events: list[dict]) -> dict:
    return {
        "greeting": f"Welcome, {user.get('name', 'Developer')}!",
        "plan": user.get("plan", "free"),
        "stats": [
            {"icon": "📱", "label": "Your Apps", "value": str(len(apps))},
            {"icon": "📊", "label": "Health", "value": f"{health_score}/100"},
            {"icon": "🔔", "label": "Notifications", "value": str(notifications)},
        ],
        "top_apps": [{"name": a.get("name", ""), "installs": a.get("installs", 0)}
                      for a in sorted(apps, key=lambda x: -x.get("installs", 0))[:3]],
        "recent_events": [{"title": e.get("title", ""), "type": e.get("type", "")}
                           for e in recent_events[:5]],
        "quick_actions": ["Create App", "View Docs", "API Keys", "Deploy"],
    }
