"""RSS feed builder — generate Atom/RSS feeds for platform updates."""
from __future__ import annotations
import html


def build_rss_feed(*, title: str, link: str, entries: list[dict],
                     description: str = "") -> dict:
    safe_title = html.escape(title)
    items = []
    for e in entries:
        items.append({
            "title": html.escape(e.get("title", "")),
            "link": e.get("link", ""),
            "description": html.escape(e.get("description", "")[:500]),
            "pub_date": e.get("date", ""),
            "category": e.get("category", ""),
            "guid": e.get("id", e.get("link", "")),
        })
    xml_header = f'<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0">\n<channel>\n<title>{safe_title}</title>\n<link>{link}</link>'
    return {"title": safe_title, "link": link, "description": html.escape(description),
            "items": items, "item_count": len(items),
            "content_type": "application/rss+xml",
            "xml_preview": xml_header}


def filter_feed(feed: dict, *, category: str | None = None,
                 limit: int = 20) -> dict:
    items = feed["items"]
    if category:
        items = [i for i in items if i["category"] == category]
    return {**feed, "items": items[:limit], "item_count": len(items[:limit]),
            "filtered": category is not None}
