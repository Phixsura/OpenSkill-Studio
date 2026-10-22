"""Notification center — manage developer notifications."""

from datetime import UTC, datetime
from collections import defaultdict

_notifications: dict[str, list[dict]] = defaultdict(list)


def add_notification(developer_id: str, *, title: str, message: str, type: str = "info", action_url: str = "") -> dict:
    n = {"title": title, "message": message, "type": type, "action_url": action_url,
         "read": False, "created_at": datetime.now(UTC).isoformat()}
    _notifications[developer_id].append(n)
    return n


def get_notifications(developer_id: str, *, unread_only: bool = False, limit: int = 20) -> list[dict]:
    notifs = _notifications.get(developer_id, [])
    if unread_only:
        notifs = [n for n in notifs if not n["read"]]
    return notifs[-limit:]


def get_unread_count(developer_id: str) -> int:
    return sum(1 for n in _notifications.get(developer_id, []) if not n["read"])


def mark_all_read(developer_id: str) -> int:
    count = 0
    for n in _notifications.get(developer_id, []):
        if not n["read"]:
            n["read"] = True
            count += 1
    return count
