"""Changelog RSS — RSS/Atom feed generator for app updates."""

import html
from datetime import datetime, timezone


def build_rss_feed(*, app_name: str, base_url: str, entries: list[dict]) -> dict:
    items_xml = []
    for e in entries:
        items_xml.append(
            f"<item><title>{html.escape(e.get('title', ''))}</title>"
            f"<link>{base_url}/changelog#{e.get('version', '')}</link>"
            f"<description>{html.escape(e.get('description', ''))}</description>"
            f"<pubDate>{e.get('date', '')}</pubDate></item>")
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>'
           f'<rss version="2.0"><channel>'
           f'<title>{html.escape(app_name)} Changelog</title>'
           f'<link>{base_url}/changelog</link>'
           f'<description>Latest updates for {html.escape(app_name)}</description>'
           f'{"".join(items_xml)}'
           f'</channel></rss>')
    return {"xml": xml, "content_type": "application/rss+xml",
            "entry_count": len(entries), "feed_url": f"{base_url}/changelog/rss"}


def build_atom_feed(*, app_name: str, base_url: str, entries: list[dict]) -> dict:
    items_xml = []
    for e in entries:
        items_xml.append(
            f'<entry><title>{html.escape(e.get("title", ""))}</title>'
            f'<link href="{base_url}/changelog#{e.get("version", "")}"/>'
            f'<summary>{html.escape(e.get("description", ""))}</summary>'
            f'<updated>{e.get("date", "")}T00:00:00Z</updated></entry>')
    xml = (f'<?xml version="1.0" encoding="UTF-8"?>'
           f'<feed xmlns="http://www.w3.org/2005/Atom">'
           f'<title>{html.escape(app_name)} Changelog</title>'
           f'<link href="{base_url}/changelog/atom" rel="self"/>'
           f'{"".join(items_xml)}</feed>')
    return {"xml": xml, "content_type": "application/atom+xml",
            "entry_count": len(entries)}
