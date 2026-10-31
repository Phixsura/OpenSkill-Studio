"""Event timeline — chronological event feed with filtering and grouping."""
from __future__ import annotations
import html


def build_event_timeline(events: list[dict], *, group_by: str | None = None,
                           limit: int = 50) -> dict:
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", ""), reverse=True)[:limit]
    items = []
    for e in sorted_events:
        items.append({
            "id": e.get("id", ""), "type": e.get("type", ""),
            "title": html.escape(e.get("title", "")),
            "description": html.escape(e.get("description", "")[:200]),
            "timestamp": e.get("timestamp", ""), "actor": e.get("actor", ""),
            "icon": _event_icon(e.get("type", "")),
        })
    groups = {}
    if group_by == "date":
        for item in items:
            date = item["timestamp"][:10] if item["timestamp"] else "Unknown"
            groups.setdefault(date, []).append(item)
    elif group_by == "type":
        for item in items:
            groups.setdefault(item["type"], []).append(item)
    return {"items": items, "total": len(items), "groups": groups if groups else None}


def _event_icon(event_type: str) -> str:
    return {"created": "✨", "updated": "📝", "deleted": "🗑️", "deployed": "🚀",
            "login": "🔑", "error": "❌", "alert": "🚨", "comment": "💬"}.get(event_type, "📌")
