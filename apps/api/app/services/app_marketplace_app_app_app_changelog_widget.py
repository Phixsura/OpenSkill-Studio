"""Changelog widget — embeddable changelog widget for apps."""

import html

TYPE_ICONS = {"added": "✨", "fixed": "🐛", "changed": "🔄", "security": "🔒", "performance": "⚡"}


def build_changelog_widget(*, app_name: str, entries: list[dict],
                              max_entries: int = 5) -> dict:
    items = []
    for e in entries[:max_entries]:
        t = e.get("type", "changed")
        items.append({
            "version": e.get("version", ""),
            "title": html.escape(e.get("title", "")),
            "type": t,
            "icon": TYPE_ICONS.get(t, "📌"),
            "date": e.get("date", ""),
        })
    has_more = len(entries) > max_entries
    return {"app_name": html.escape(app_name), "entries": items,
            "shown": len(items), "total": len(entries),
            "has_more": has_more}
