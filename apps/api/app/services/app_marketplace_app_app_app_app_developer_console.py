"""Developer console — the ultimate developer console with all tools."""

import html
from datetime import datetime, timezone


def build_developer_console(*, user: dict, org: dict, apps: list[dict],
                               notifications: int = 0) -> dict:
    total_installs = sum(a.get("installs", 0) for a in apps)
    total_api = sum(a.get("api_calls", 0) for a in apps)
    hour = datetime.now(timezone.utc).hour
    greeting = "Good morning" if hour < 12 else "Good afternoon" if hour < 18 else "Good evening"
    return {
        "greeting": f"{greeting}, {html.escape(user.get('name', ''))}!",
        "console_sections": [
            {"id": "apps", "label": "My Apps", "icon": "📦", "count": len(apps), "href": "/apps"},
            {"id": "analytics", "label": "Analytics", "icon": "📊", "count": None, "href": "/analytics"},
            {"id": "webhooks", "label": "Webhooks", "icon": "🔗", "count": None, "href": "/webhooks"},
            {"id": "api_keys", "label": "API Keys", "icon": "🔑", "count": None, "href": "/keys"},
            {"id": "team", "label": "Team", "icon": "👥", "count": org.get("member_count"), "href": "/team"},
            {"id": "billing", "label": "Billing", "icon": "💳", "count": None, "href": "/billing"},
            {"id": "settings", "label": "Settings", "icon": "⚙️", "count": None, "href": "/settings"},
            {"id": "docs", "label": "Docs", "icon": "📖", "count": None, "href": "/docs"},
        ],
        "stats": [
            {"label": "Apps", "value": len(apps), "icon": "📦"},
            {"label": "Installs", "value": total_installs, "display": f"{total_installs:,}", "icon": "📥"},
            {"label": "API Calls", "value": total_api, "display": f"{total_api:,}", "icon": "🔗"},
            {"label": "Team", "value": org.get("member_count", 1), "icon": "👥"},
        ],
        "org": {"name": html.escape(org.get("name", "")), "plan": org.get("plan", "free")},
        "notifications": notifications,
    }
