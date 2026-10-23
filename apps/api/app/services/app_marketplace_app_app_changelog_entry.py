"""Changelog entry — structured changelog entries with categories."""

import html
from datetime import datetime


def create_changelog_entry(*, version: str, date: str | None = None,
                              changes: list[dict]) -> dict:
    d = date or datetime.utcnow().strftime("%Y-%m-%d")
    categorized: dict[str, list] = {}
    for change in changes:
        cat = change.get("type", "other")
        desc = html.escape(change.get("description", ""))
        categorized.setdefault(cat, []).append(desc)
    return {
        "version": version,
        "date": d,
        "categories": [{"type": k, "items": v} for k, v in categorized.items()],
        "total_changes": len(changes),
        "has_breaking": any(c.get("breaking") for c in changes),
    }
