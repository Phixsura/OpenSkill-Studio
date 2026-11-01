"""User activity log — personal activity history."""

import html
from datetime import datetime, timezone
from collections import defaultdict

ACTION_LABELS = {
    "login": "Logged in", "logout": "Logged out", "create_app": "Created app",
    "deploy": "Deployed", "update_settings": "Updated settings",
    "invite_member": "Invited member", "create_webhook": "Created webhook",
    "generate_key": "Generated API key", "delete_app": "Deleted app",
}
ACTION_ICONS = {
    "login": "🔑", "logout": "👋", "create_app": "📦", "deploy": "🚀",
    "update_settings": "⚙️", "invite_member": "👤", "create_webhook": "🔗",
    "generate_key": "🔐", "delete_app": "🗑️",
}


def build_activity_log(*, activities: list[dict], limit: int = 50) -> dict:
    items = []
    by_day: dict[str, int] = defaultdict(int)
    for a in activities[:limit]:
        action = a.get("action", "unknown")
        day = a.get("timestamp", "")[:10]
        by_day[day] += 1
        items.append({
            "action": action,
            "label": ACTION_LABELS.get(action, action.replace("_", " ").title()),
            "icon": ACTION_ICONS.get(action, "📌"),
            "target": html.escape(a.get("target", "")),
            "timestamp": a.get("timestamp", ""),
            "ip": a.get("ip", ""),
        })
    return {"activities": items, "total": len(items),
            "by_day": dict(by_day), "active_days": len(by_day)}
