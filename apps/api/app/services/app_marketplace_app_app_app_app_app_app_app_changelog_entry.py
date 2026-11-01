"""Changelog entry builder — create structured changelog entries."""
from __future__ import annotations
import html


ENTRY_TYPES = {
    "added": {"emoji": "✨", "label": "Added", "color": "green"},
    "changed": {"emoji": "🔄", "label": "Changed", "color": "blue"},
    "fixed": {"emoji": "🐛", "label": "Fixed", "color": "orange"},
    "removed": {"emoji": "🗑️", "label": "Removed", "color": "red"},
    "deprecated": {"emoji": "⚠️", "label": "Deprecated", "color": "yellow"},
    "security": {"emoji": "🔒", "label": "Security", "color": "purple"},
}


def create_entry(*, entry_type: str, title: str, description: str = "",
                   version: str = "", breaking: bool = False) -> dict:
    type_info = ENTRY_TYPES.get(entry_type, ENTRY_TYPES["changed"])
    return {
        "type": entry_type, "emoji": type_info["emoji"], "label": type_info["label"],
        "color": type_info["color"],
        "title": html.escape(title), "description": html.escape(description[:500]),
        "version": version, "breaking": breaking,
    }


def group_entries(entries: list[dict]) -> dict:
    groups: dict[str, list[dict]] = {}
    for e in entries:
        groups.setdefault(e["type"], []).append(e)
    sections = []
    for etype in ("added", "changed", "fixed", "security", "deprecated", "removed"):
        if etype in groups:
            info = ENTRY_TYPES.get(etype, {})
            sections.append({"type": etype, "emoji": info.get("emoji", ""),
                              "label": info.get("label", etype),
                              "entries": groups[etype], "count": len(groups[etype])})
    has_breaking = any(e["breaking"] for e in entries)
    return {"sections": sections, "total": len(entries), "has_breaking": has_breaking}
