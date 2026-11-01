"""App notification badge — notification count badge with categories."""

import html
from collections import defaultdict


def build_notification_badge(*, notifications: list[dict]) -> dict:
    unread = sum(1 for n in notifications if not n.get("read"))
    by_category: dict[str, int] = defaultdict(int)
    urgent = 0
    for n in notifications:
        if not n.get("read"):
            by_category[n.get("category", "general")] += 1
            if n.get("priority") == "urgent":
                urgent += 1
    return {
        "total": len(notifications), "unread": unread, "urgent": urgent,
        "by_category": dict(by_category),
        "display": str(unread) if unread <= 99 else "99+",
        "has_unread": unread > 0, "has_urgent": urgent > 0,
    }
