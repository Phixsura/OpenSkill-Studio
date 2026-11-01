"""Changelog RSS — generate RSS/Atom feeds for app updates."""

from xml.sax.saxutils import escape
from datetime import datetime


def generate_rss_feed(*, app_name: str, app_id: str, entries: list[dict]) -> dict:
    safe_name = escape(app_name)
    items_xml = []
    for entry in entries:
        items_xml.append(
            f"    <item>\n"
            f"      <title>{escape(entry.get('title', ''))}</title>\n"
            f"      <description>{escape(entry.get('description', ''))}</description>\n"
            f"      <pubDate>{escape(entry.get('date', ''))}</pubDate>\n"
            f"      <guid>https://marketplace.openskill.dev/apps/{escape(app_id)}/changelog/{escape(entry.get('version', ''))}</guid>\n"
            f"    </item>"
        )
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<rss version="2.0">\n'
        '  <channel>\n'
        f'    <title>{safe_name} Changelog</title>\n'
        f'    <link>https://marketplace.openskill.dev/apps/{escape(app_id)}</link>\n'
        f'    <description>Updates for {safe_name}</description>\n'
        + "\n".join(items_xml) + "\n"
        '  </channel>\n'
        '</rss>'
    )
    return {"xml": xml, "content_type": "application/rss+xml",
            "item_count": len(entries)}
