"""App notifications page — full notification center with tabs."""

import html
from collections import defaultdict


def build_notifications_page(*, notifications: list[dict]) -> dict:
    tabs: dict[str, list] = defaultdict(list)
    unread_count = 0
    for n in notifications:
        cat = n.get("category", "general")
        is_read = n.get("read", False)
        if not is_read:
            unread_count += 1
        tabs[cat].append({
            "id": n.get("id", ""), "title": html.escape(n.get("title", "")),
            "body": html.escape(n.get("body", "")),
            "icon": n.get("icon", "🔔"), "read": is_read,
            "timestamp": n.get("timestamp", ""),
            "action_url": n.get("action_url"),
        })
    tab_list = [{"id": cat, "label": cat.replace("_", " ").title(),
                  "count": len(items), "unread": sum(1 for i in items if not i["read"])}
                 for cat, items in tabs.items()]
    return {"tabs": tab_list, "notifications_by_tab": dict(tabs),
            "total": len(notifications), "unread": unread_count}
