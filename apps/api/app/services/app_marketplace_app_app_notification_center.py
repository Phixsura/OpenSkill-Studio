"""Notification center — grouped notification management."""

import html
from datetime import datetime, timezone


def build_notification_center(*, notifications: list[dict]) -> dict:
    items = []
    unread = 0
    for n in notifications:
        read = n.get("read", False)
        if not read:
            unread += 1
        items.append({
            "id": n["id"],
            "title": html.escape(n.get("title", "")),
            "body": html.escape(n.get("body", "")),
            "icon": n.get("icon", "🔔"),
            "type": n.get("type", "info"),
            "read": read,
            "timestamp": n.get("timestamp", datetime.now(timezone.utc).isoformat()),
        })
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"notifications": items, "total": len(items), "unread": unread}


def mark_read(*, notifications: list[dict], ids: list[str]) -> dict:
    id_set = set(ids)
    updated = 0
    for n in notifications:
        if n["id"] in id_set and not n.get("read", False):
            n["read"] = True
            updated += 1
    return {"updated": updated}
