"""Notification center — unified notification inbox for developers."""

import secrets
from datetime import datetime


NOTIFICATION_TYPES = {
    "info": {"icon": "ℹ️", "priority": 0},
    "success": {"icon": "✅", "priority": 0},
    "warning": {"icon": "⚠️", "priority": 1},
    "error": {"icon": "❌", "priority": 2},
    "action_required": {"icon": "🔔", "priority": 3},
}


def create_notification(*, user_id: str, title: str, message: str,
                          ntype: str = "info", action_url: str | None = None) -> dict:
    type_info = NOTIFICATION_TYPES.get(ntype, NOTIFICATION_TYPES["info"])
    return {
        "notification_id": f"notif_{secrets.token_urlsafe(8)}",
        "user_id": user_id,
        "title": title,
        "message": message,
        "type": ntype,
        "icon": type_info["icon"],
        "priority": type_info["priority"],
        "action_url": action_url,
        "read": False,
        "created_at": datetime.utcnow().isoformat(),
    }


def get_notification_summary(*, notifications: list[dict]) -> dict:
    unread = sum(1 for n in notifications if not n.get("read"))
    by_type: dict[str, int] = {}
    for n in notifications:
        t = n.get("type", "info")
        by_type[t] = by_type.get(t, 0) + 1
    action_required = sum(1 for n in notifications if n.get("type") == "action_required" and not n.get("read"))
    return {"total": len(notifications), "unread": unread,
            "action_required": action_required, "by_type": by_type}
