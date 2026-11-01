"""Changelog — version release notes builder."""

import html
from datetime import datetime, timezone

TYPES = {"feat": "✨", "fix": "🐛", "perf": "⚡", "docs": "📝", "breaking": "💥"}


def build_changelog(*, releases: list[dict]) -> dict:
    items = []
    for rel in releases:
        entries = []
        for e in rel.get("entries", []):
            t = e.get("type", "feat")
            entries.append({
                "type": t,
                "icon": TYPES.get(t, "📌"),
                "message": html.escape(e.get("message", "")),
                "breaking": t == "breaking",
            })
        items.append({
            "version": rel["version"],
            "date": rel.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
            "entries": entries,
            "entry_count": len(entries),
            "has_breaking": any(e["breaking"] for e in entries),
        })
    return {"releases": items, "total_releases": len(items),
            "latest": items[0]["version"] if items else None}
