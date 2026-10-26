"""Changelog RSS — generate RSS/Atom feeds for extension changelogs.

Produces syndication feeds so developers and users can subscribe
to extension updates via their preferred RSS reader.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
import html


@dataclass
class ChangelogItem:
    version: str
    title: str
    description: str
    published_at: str
    author: str
    link: str = ""


class ChangelogRSSGenerator:
    """Generates RSS and Atom feeds for extension changelogs."""

    def __init__(self, base_url: str = "https://marketplace.openskill.dev"):
        self._base_url = base_url
        self._feeds: dict[str, list[ChangelogItem]] = {}

    def add_entry(self, extension_id: str, item: ChangelogItem) -> None:
        self._feeds.setdefault(extension_id, []).append(item)

    def generate_rss(self, extension_id: str, title: str = "",
                     max_items: int = 20) -> str:
        """Generate RSS 2.0 XML feed."""
        items = self._feeds.get(extension_id, [])[-max_items:]
        feed_title = title or f"{extension_id} Changelog"
        feed_link = f"{self._base_url}/extensions/{extension_id}/changelog"

        xml_items = []
        for item in reversed(items):
            link = item.link or f"{feed_link}#{item.version}"
            xml_items.append(
                f"    <item>\n"
                f"      <title>{html.escape(item.title)}</title>\n"
                f"      <description>{html.escape(item.description)}</description>\n"
                f"      <link>{html.escape(link)}</link>\n"
                f"      <pubDate>{item.published_at}</pubDate>\n"
                f"      <author>{html.escape(item.author)}</author>\n"
                f"      <guid>{html.escape(link)}</guid>\n"
                f"    </item>"
            )

        return (
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0">\n'
            '  <channel>\n'
            f'    <title>{html.escape(feed_title)}</title>\n'
            f'    <link>{html.escape(feed_link)}</link>\n'
            f'    <description>Changelog for {html.escape(extension_id)}</description>\n'
            + "\n".join(xml_items) + "\n"
            '  </channel>\n'
            '</rss>'
        )

    def generate_json_feed(self, extension_id: str, title: str = "",
                           max_items: int = 20) -> dict:
        """Generate JSON Feed (1.1) format."""
        items = self._feeds.get(extension_id, [])[-max_items:]
        feed_title = title or f"{extension_id} Changelog"
        return {
            "version": "https://jsonfeed.org/version/1.1",
            "title": feed_title,
            "home_page_url": f"{self._base_url}/extensions/{extension_id}",
            "feed_url": f"{self._base_url}/extensions/{extension_id}/feed.json",
            "items": [
                {
                    "id": item.version,
                    "title": item.title,
                    "content_text": item.description,
                    "date_published": item.published_at,
                    "authors": [{"name": item.author}],
                    "url": item.link or f"{self._base_url}/extensions/{extension_id}/changelog#{item.version}",
                }
                for item in reversed(items)
            ],
        }

    def get_latest(self, extension_id: str) -> ChangelogItem | None:
        items = self._feeds.get(extension_id, [])
        return items[-1] if items else None

    def get_feed_urls(self, extension_id: str) -> dict:
        return {
            "rss": f"{self._base_url}/extensions/{extension_id}/feed.xml",
            "json": f"{self._base_url}/extensions/{extension_id}/feed.json",
            "atom": f"{self._base_url}/extensions/{extension_id}/feed.atom",
        }
