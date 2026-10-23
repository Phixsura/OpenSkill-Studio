"""App changelog viewer — display per-app changelogs with version grouping."""
from __future__ import annotations
import html

CHANGE_ICONS = {"added": "✨", "fixed": "🐛", "changed": "🔄", "removed": "🗑️",
                 "security": "🔒", "performance": "⚡", "deprecated": "⚠️"}


def format_changelog(versions: list[dict]) -> dict:
    formatted = []
    total_changes = 0
    for v in versions:
        changes = v.get("changes", [])
        total_changes += len(changes)
        formatted.append({
            "version": v["version"], "date": v.get("date", ""),
            "summary": html.escape(v.get("summary", "")),
            "changes": [{"type": c.get("type", "changed"),
                          "icon": CHANGE_ICONS.get(c.get("type", ""), "📌"),
                          "text": html.escape(c.get("text", ""))}
                         for c in changes],
            "change_count": len(changes),
        })
    return {"versions": formatted, "total_versions": len(formatted),
            "total_changes": total_changes}
