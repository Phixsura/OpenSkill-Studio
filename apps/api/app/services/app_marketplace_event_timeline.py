"""Event timeline — build activity feed for app or developer."""

from datetime import datetime, timezone

EVENT_ICONS = {
    "install": "📥", "uninstall": "📤", "update": "🔄", "review": "⭐",
    "version_published": "🚀", "config_change": "⚙️", "error": "❌",
}


def build_timeline(*, events: list[dict], limit: int = 50) -> dict:
    sorted_events = sorted(events, key=lambda e: e.get("timestamp", ""), reverse=True)[:limit]
    items = []
    for e in sorted_events:
        items.append({
            "type": e["type"], "icon": EVENT_ICONS.get(e["type"], "📌"),
            "title": e.get("title", e["type"].replace("_", " ").title()),
            "description": e.get("description", ""),
            "timestamp": e.get("timestamp"), "actor": e.get("actor"),
            "metadata": {k: v for k, v in e.items() if k not in ("type", "title", "description", "timestamp", "actor")},
        })
    return {"items": items, "total": len(events), "showing": len(items)}


def group_by_date(*, timeline_items: list[dict]) -> dict:
    groups: dict[str, list] = {}
    for item in timeline_items:
        ts = item.get("timestamp", "")
        date = ts[:10] if len(ts) >= 10 else "unknown"
        groups.setdefault(date, []).append(item)
    return {"groups": [{"date": d, "events": evts} for d, evts in groups.items()]}
