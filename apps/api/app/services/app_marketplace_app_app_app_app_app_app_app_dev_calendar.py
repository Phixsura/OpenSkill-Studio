"""Developer event calendar — track upcoming events, launches, and milestones."""
from __future__ import annotations
import html

EVENT_TYPES = {
    "release": {"icon": "🚀", "color": "blue"},
    "webinar": {"icon": "🎥", "color": "purple"},
    "hackathon": {"icon": "💻", "color": "green"},
    "maintenance": {"icon": "🔧", "color": "yellow"},
    "deadline": {"icon": "⏰", "color": "red"},
    "milestone": {"icon": "🏆", "color": "orange"},
}


def build_calendar(events: list[dict]) -> dict:
    items = []
    by_month: dict[str, list[dict]] = {}
    for e in events:
        evt_type = e.get("type", "release")
        type_info = EVENT_TYPES.get(evt_type, EVENT_TYPES["release"])
        item = {
            "title": html.escape(e.get("title", "")),
            "date": e.get("date", ""), "type": evt_type,
            "icon": type_info["icon"], "color": type_info["color"],
            "description": html.escape(e.get("description", "")[:200]),
        }
        items.append(item)
        month = e.get("date", "")[:7]
        by_month.setdefault(month, []).append(item)
    return {"events": items, "total": len(items), "by_month": by_month,
            "months": sorted(by_month.keys())}


def upcoming_events(events: list[dict], *, after_date: str = "", limit: int = 5) -> list[dict]:
    filtered = [e for e in events if e.get("date", "") >= after_date] if after_date else events
    return sorted(filtered, key=lambda e: e.get("date", ""))[:limit]
