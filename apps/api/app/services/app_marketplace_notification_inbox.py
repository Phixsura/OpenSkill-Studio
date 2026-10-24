"""Notification inbox — unified inbox for all marketplace notifications."""

from datetime import datetime, timezone


def get_inbox(*, notifications: list[dict], unread_only: bool = False,
                category: str | None = None, limit: int = 50) -> dict:
    result = notifications
    if unread_only:
        result = [n for n in result if not n.get("read")]
    if category:
        result = [n for n in result if n.get("category") == category]
    sorted_notifs = sorted(result, key=lambda n: n.get("created_at", ""), reverse=True)[:limit]
    unread = sum(1 for n in notifications if not n.get("read"))
    return {"notifications": sorted_notifs, "showing": len(sorted_notifs),
            "total": len(notifications), "unread": unread}


def mark_read(*, notification_id: str, notifications: list[dict]) -> list[dict]:
    return [{**n, "read": True} if n.get("id") == notification_id else n for n in notifications]


def mark_all_read(*, notifications: list[dict]) -> list[dict]:
    return [{**n, "read": True} for n in notifications]


def group_by_date(*, notifications: list[dict]) -> list[dict]:
    groups: dict[str, list] = {}
    for n in notifications:
        date = n.get("created_at", "")[:10]
        groups.setdefault(date, []).append(n)
    return [{"date": d, "notifications": ns, "count": len(ns)}
            for d, ns in sorted(groups.items(), reverse=True)]
