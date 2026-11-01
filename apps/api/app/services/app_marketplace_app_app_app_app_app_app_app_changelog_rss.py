"""Changelog RSS feed — generate RSS from changelog entries."""
from __future__ import annotations
import html


def generate_rss(title: str, link: str, entries: list[dict]) -> dict:
    safe_title = html.escape(title)
    safe_link = html.escape(link)
    items_xml = []
    for e in entries:
        items_xml.append(
            f"<item><title>{html.escape(e.get('title', ''))}</title>"
            f"<description>{html.escape(e.get('description', ''))}</description>"
            f"<pubDate>{html.escape(e.get('date', ''))}</pubDate>"
            f"<guid>{html.escape(e.get('id', ''))}</guid></item>"
        )
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>'
           f'<rss version="2.0"><channel>'
           f'<title>{safe_title}</title><link>{safe_link}</link>'
           f'{"".join(items_xml)}</channel></rss>')
    return {"xml": xml, "item_count": len(entries), "title": safe_title}


def parse_entries(releases: list[dict]) -> list[dict]:
    return [{"id": r.get("version", ""), "title": f"v{r.get('version', '')}",
             "description": r.get("summary", ""), "date": r.get("date", "")}
            for r in releases]
