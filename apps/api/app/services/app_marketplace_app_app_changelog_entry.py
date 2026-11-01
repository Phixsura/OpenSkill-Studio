"""Changelog entry — individual changelog entry builder."""

import html
from datetime import datetime, timezone

TYPES = {"added": "✨", "changed": "🔄", "fixed": "🐛", "removed": "🗑️",
         "deprecated": "⚠️", "security": "🔒", "performance": "⚡"}


def create_entry(*, type: str, title: str, description: str = "",
                   pr_number: int | None = None, author: str = "") -> dict:
    return {
        "type": type, "icon": TYPES.get(type, "📌"),
        "title": html.escape(title), "description": html.escape(description),
        "pr_number": pr_number, "author": html.escape(author),
        "created_at": datetime.now(timezone.utc).isoformat(),
    }


def group_entries(*, entries: list[dict]) -> dict:
    groups: dict[str, list] = {}
    for e in entries:
        t = e.get("type", "changed")
        groups.setdefault(t, []).append(e)
    order = ["added", "changed", "fixed", "performance", "security", "deprecated", "removed"]
    sorted_groups = [(t, groups[t]) for t in order if t in groups]
    for t in groups:
        if t not in order:
            sorted_groups.append((t, groups[t]))
    return {"groups": [{"type": t, "icon": TYPES.get(t, "📌"), "label": t.title(),
                          "entries": entries, "count": len(entries)}
                         for t, entries in sorted_groups],
            "total": len(entries)}
