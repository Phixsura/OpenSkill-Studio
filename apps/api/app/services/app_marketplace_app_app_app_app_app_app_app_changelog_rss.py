"""Changelog RSS — generate RSS feed from platform changelog entries."""
from __future__ import annotations
import html


def build_changelog_rss(entries: list[dict], *, title: str = "OpenSkill Changelog",
                          base_url: str = "https://openskill.io") -> dict:
    items = []
    for e in entries:
        items.append({
            "title": html.escape(e.get("title", "")),
            "version": e.get("version", ""),
            "date": e.get("date", ""),
            "description": html.escape(e.get("description", "")[:500]),
            "link": f"{base_url}/changelog/{e.get('version', '')}",
            "change_count": e.get("change_count", 0),
        })
    return {"title": title, "items": items, "item_count": len(items),
            "last_updated": items[0]["date"] if items else ""}
