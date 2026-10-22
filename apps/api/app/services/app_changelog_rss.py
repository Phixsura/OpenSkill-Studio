"""Changelog RSS feed generator."""

from datetime import UTC, datetime


def build_rss_feed(*, app_name: str, app_slug: str, entries: list[dict], base_url: str = "https://marketplace.openskill.studio") -> str:
    items = []
    for entry in entries:
        items.append(f"""    <item>
      <title>{app_name} v{entry['version']}</title>
      <link>{base_url}/apps/{app_slug}/changelog#{entry['version']}</link>
      <description>{entry.get('notes', 'New version released')}</description>
      <pubDate>{entry.get('date', datetime.now(UTC).isoformat())}</pubDate>
    </item>""")
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>{app_name} Changelog</title>
    <link>{base_url}/apps/{app_slug}</link>
    <description>Release notes for {app_name}</description>
{''.join(items)}
  </channel>
</rss>"""
