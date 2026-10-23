"""Timeline — chronological event feed."""

import html
from datetime import datetime, timezone


def build_timeline(*, events: list[dict]) -> dict:
    items = []
    for e in events:
        ts = e.get("timestamp") or datetime.now(timezone.utc).isoformat()
        items.append({
            "id": e.get("id", ""),
            "title": html.escape(e.get("title", "")),
            "description": html.escape(e.get("description", "")),
            "icon": e.get("icon", "📌"),
            "timestamp": ts,
            "actor": html.escape(e.get("actor", "System")),
            "type": e.get("type", "info"),
        })
    items.sort(key=lambda x: x["timestamp"], reverse=True)
    return {"items": items, "count": len(items)}
