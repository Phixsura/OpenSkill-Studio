"""Platform notification center — unified notification management."""
from __future__ import annotations
import html
import time

_notifications: list[dict] = []


def send_notification(recipient: str, title: str, body: str,
                       category: str = "info", priority: str = "normal") -> dict:
    notif = {"id": len(_notifications) + 1, "recipient": recipient,
             "title": html.escape(title), "body": html.escape(body),
             "category": category, "priority": priority,
             "read": False, "created_at": time.time()}
    _notifications.append(notif)
    return notif


def get_notifications(recipient: str, unread_only: bool = False) -> dict:
    items = [n for n in _notifications if n["recipient"] == recipient]
    if unread_only:
        items = [n for n in items if not n["read"]]
    return {"notifications": list(reversed(items[-20:])), "total": len(items),
            "unread": sum(1 for n in items if not n["read"])}


def mark_read(notification_id: int) -> dict:
    for n in _notifications:
        if n["id"] == notification_id:
            n["read"] = True
            return {"marked": True}
    return {"marked": False, "error": "not_found"}


def clear_notifications() -> None:
    _notifications.clear()
