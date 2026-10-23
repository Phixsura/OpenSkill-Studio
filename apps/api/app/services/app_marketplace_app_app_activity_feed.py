"""Activity feed — real-time activity stream with grouping."""

import html
from datetime import datetime, timezone


VERBS = {
    "install": "installed", "uninstall": "uninstalled", "review": "reviewed",
    "publish": "published", "update": "updated", "comment": "commented on",
}


def build_activity_feed(*, activities: list[dict], limit: int = 20) -> dict:
    items = []
    for a in activities[:limit]:
        verb = a.get("verb", "did something")
        items.append({
            "id": a.get("id", ""),
            "actor": html.escape(a.get("actor", "Someone")),
            "verb": VERBS.get(verb, verb),
            "target": html.escape(a.get("target", "")),
            "icon": a.get("icon", "📌"),
            "timestamp": a.get("timestamp", datetime.now(timezone.utc).isoformat()),
            "metadata": a.get("metadata", {}),
        })
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"activities": items, "count": len(items), "has_more": len(activities) > limit}
