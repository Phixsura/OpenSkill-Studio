"""Notification center page — full notification management page."""

import html
from collections import defaultdict


def build_notification_center_page(*, notifications: list[dict]) -> dict:
    items = []
    unread = 0
    by_category: dict[str, int] = defaultdict(int)
    for n in notifications:
        is_read = n.get("read", False)
        if not is_read:
            unread += 1
        cat = n.get("category", "general")
        by_category[cat] += 1
        items.append({
            "id": n.get("id", ""), "title": html.escape(n.get("title", "")),
            "body": html.escape(n.get("body", "")),
            "icon": n.get("icon", "🔔"), "category": cat,
            "read": is_read, "timestamp": n.get("timestamp", ""),
            "action_url": n.get("action_url"),
        })
    categories = [{"id": cat, "label": cat.replace("_", " ").title(), "count": count,
                    "unread": sum(1 for i in items if i["category"] == cat and not i["read"])}
                   for cat, count in sorted(by_category.items())]
    return {"notifications": items[:50], "total": len(items), "unread": unread,
            "categories": categories, "has_unread": unread > 0}
