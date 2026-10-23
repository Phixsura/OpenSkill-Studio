"""Atom feed builder — generate Atom XML feeds for app changelogs."""
from __future__ import annotations
import html


def build_atom_feed(*, title: str, app_id: str, entries: list[dict],
                      base_url: str = "https://marketplace.openskill.io") -> dict:
    safe_title = html.escape(title)
    feed_url = f"{base_url}/apps/{app_id}/changelog.atom"
    items = []
    for e in entries:
        items.append({
            "title": html.escape(e.get("title", "")),
            "version": e.get("version", ""),
            "date": e.get("date", ""),
            "summary": html.escape(e.get("summary", "")[:500]),
            "url": f"{base_url}/apps/{app_id}/changelog/{e.get('version', '')}",
        })
    return {"title": safe_title, "feed_url": feed_url, "items": items,
            "item_count": len(items), "content_type": "application/atom+xml",
            "updated": items[0]["date"] if items else ""}


def generate_atom_xml(feed: dict) -> str:
    lines = [f'<?xml version="1.0" encoding="UTF-8"?>',
             f'<feed xmlns="http://www.w3.org/2005/Atom">',
             f'  <title>{feed["title"]}</title>',
             f'  <link href="{html.escape(feed["feed_url"])}" rel="self"/>']
    for item in feed["items"]:
        lines.extend([f'  <entry>', f'    <title>{item["title"]}</title>',
                       f'    <link href="{html.escape(item["url"])}"/>',
                       f'    <updated>{item["date"]}</updated>',
                       f'    <summary>{item["summary"]}</summary>', f'  </entry>'])
    lines.append('</feed>')
    return "\n".join(lines)
