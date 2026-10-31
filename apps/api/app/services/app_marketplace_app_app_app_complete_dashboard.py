"""Complete dashboard — the ultimate OpenSkill Developer Platform dashboard."""

import html
from datetime import datetime, timezone


def build_complete_dashboard(*, user: dict, org: dict, apps: list[dict],
                                notifications: int = 0) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_reviews = sum(a.get("review_count", 0) for a in apps)
    avg_rating = round(sum(a.get("rating", 0) for a in apps) / max(len(apps), 1), 1) if apps else 0
    hour = datetime.now(timezone.utc).hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    top_app = max(apps, key=lambda a: a.get("installs", 0)) if apps else None
    return {
        "greeting": f"{greeting}, {html.escape(user.get('name', ''))}!",
        "org": {"name": html.escape(org.get("name", "")), "plan": org.get("plan", "free"),
                "member_count": org.get("member_count", 1)},
        "quick_stats": [
            {"label": "Apps", "value": len(apps), "icon": "📦"},
            {"label": "Installs", "value": total_installs, "display": f"{total_installs:,}", "icon": "📥"},
            {"label": "Reviews", "value": total_reviews, "icon": "⭐"},
            {"label": "Avg Rating", "value": avg_rating, "display": f"{avg_rating}/5", "icon": "💫"},
            {"label": "Notifications", "value": notifications, "icon": "🔔"},
        ],
        "top_app": {"name": html.escape(top_app.get("name", "")), "icon": top_app.get("icon", "📦"),
                      "installs": top_app.get("installs", 0)} if top_app else None,
        "recent_apps": [{"id": a.get("id"), "name": html.escape(a.get("name", "")),
                          "icon": a.get("icon", "📦"), "status": a.get("status", "active")}
                         for a in apps[:5]],
        "quick_actions": [
            {"label": "Create App", "href": "/apps/new", "icon": "➕"},
            {"label": "View Analytics", "href": "/analytics", "icon": "📊"},
            {"label": "API Docs", "href": "/docs/api", "icon": "📋"},
            {"label": "Support", "href": "/support", "icon": "🛟"},
        ],
        "platform": "OpenSkill Developer Platform",
        "version": "10.0.0",
    }
