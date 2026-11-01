"""Developer inbox — unified message center for developer communications."""

import secrets
from datetime import datetime


MESSAGE_TYPES = {
    "review": {"icon": "⭐", "label": "New Review"},
    "install": {"icon": "📥", "label": "New Install"},
    "support": {"icon": "💬", "label": "Support Request"},
    "system": {"icon": "🔔", "label": "System Notification"},
    "billing": {"icon": "💰", "label": "Billing Update"},
    "security": {"icon": "🔒", "label": "Security Alert"},
}


def create_message(*, msg_type: str, title: str, body: str,
                     app_id: str | None = None) -> dict:
    info = MESSAGE_TYPES.get(msg_type, {"icon": "📌", "label": "Message"})
    return {
        "message_id": f"msg_{secrets.token_urlsafe(8)}",
        "type": msg_type,
        "type_label": info["label"],
        "icon": info["icon"],
        "title": title,
        "body": body,
        "app_id": app_id,
        "read": False,
        "created_at": datetime.utcnow().isoformat(),
    }


def get_inbox_summary(*, messages: list[dict]) -> dict:
    unread = sum(1 for m in messages if not m.get("read"))
    by_type: dict[str, int] = {}
    for m in messages:
        t = m.get("type", "system")
        by_type[t] = by_type.get(t, 0) + 1
    priority_unread = sum(1 for m in messages
                          if not m.get("read") and m.get("type") in ("security", "support"))
    return {"total": len(messages), "unread": unread,
            "priority_unread": priority_unread, "by_type": by_type}
