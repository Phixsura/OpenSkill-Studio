"""Changelog widget — embeddable widget showing latest platform changes."""
from __future__ import annotations
import html


def build_widget(changes: list[dict], *, max_items: int = 5) -> dict:
    items = []
    for c in changes[:max_items]:
        items.append({
            "version": c.get("version", ""),
            "title": html.escape(c.get("title", "")),
            "type": c.get("type", "changed"),
            "date": c.get("date", ""),
        })
    return {"items": items, "count": len(items), "total": len(changes),
            "has_more": len(changes) > max_items}


def format_type_badge(change_type: str) -> dict:
    badges = {
        "added": {"emoji": "✨", "color": "green", "label": "New"},
        "fixed": {"emoji": "🐛", "color": "orange", "label": "Fix"},
        "changed": {"emoji": "🔄", "color": "blue", "label": "Update"},
        "removed": {"emoji": "🗑️", "color": "red", "label": "Removed"},
        "security": {"emoji": "🔒", "color": "purple", "label": "Security"},
    }
    return badges.get(change_type, {"emoji": "📌", "color": "gray", "label": change_type})
