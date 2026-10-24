"""Changelog timeline — organize releases into a visual timeline."""
from __future__ import annotations
import html


def build_timeline(releases: list[dict]) -> dict:
    items = []
    for r in releases:
        changes = r.get("changes", [])
        breaking = sum(1 for c in changes if c.get("breaking"))
        items.append({
            "version": r["version"], "date": r.get("date", ""),
            "title": html.escape(r.get("title", f"v{r['version']}")),
            "changes_count": len(changes),
            "breaking_count": breaking,
            "highlight": r.get("highlight", False),
            "tags": r.get("tags", []),
        })
    return {"releases": items, "total": len(items),
            "latest": items[0]["version"] if items else None}
