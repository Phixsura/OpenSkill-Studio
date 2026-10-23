"""App changelog viewer — complete changelog viewer for app detail pages."""

import html
from datetime import datetime, timezone


def build_changelog_viewer(*, app_name: str, releases: list[dict]) -> dict:
    items = []
    total_changes = 0
    for r in sorted(releases, key=lambda x: x.get("date", ""), reverse=True):
        entries = r.get("entries", [])
        total_changes += len(entries)
        items.append({
            "version": r["version"],
            "date": r.get("date", ""),
            "entry_count": len(entries),
            "entries": [{"type": e.get("type", "changed"), "text": html.escape(e.get("text", ""))}
                         for e in entries],
            "has_breaking": any(e.get("type") == "breaking" for e in entries),
        })
    return {"app_name": html.escape(app_name), "releases": items,
            "total_releases": len(items), "total_changes": total_changes,
            "latest": items[0]["version"] if items else None}
