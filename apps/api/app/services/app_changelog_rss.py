"""App Changelog RSS — generate RSS feeds from app changelogs.

Generates RSS/Atom feeds for app releases:
- Build RSS 2.0 XML from release entries
- Configurable feed metadata
- Per-installation scoped feeds
"""

from __future__ import annotations

import html
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FeedItem:
    """A single RSS feed item."""

    title: str
    description: str
    version: str
    date: str  # ISO date
    link: str = ""


@dataclass
class FeedConfig:
    """RSS feed configuration."""

    title: str
    description: str
    link: str
    language: str = "en"


class AppChangelogRSS:
    """Generate RSS feeds from app changelogs."""

    def __init__(self) -> None:
        self._configs: dict[str, FeedConfig] = {}
        self._items: dict[str, list[FeedItem]] = {}

    def configure_feed(
        self,
        installation_id: str,
        title: str,
        description: str,
        link: str,
        language: str = "en",
    ) -> FeedConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not title:
            raise ValueError("title is required")
        if not link:
            raise ValueError("link is required")

        config = FeedConfig(title=title, description=description,
                            link=link, language=language)
        self._configs[installation_id] = config
        return config

    def add_item(
        self,
        installation_id: str,
        title: str,
        description: str,
        version: str,
        date: str,
        link: str = "",
    ) -> FeedItem:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not title:
            raise ValueError("title is required")

        item = FeedItem(title=title, description=description,
                        version=version, date=date, link=link)
        self._items.setdefault(installation_id, []).append(item)
        return item

    def generate_rss(self, installation_id: str, limit: int = 20) -> str:
        """Generate RSS 2.0 XML string."""
        config = self._configs.get(installation_id)
        if config is None:
            raise KeyError(f"Feed not configured for {installation_id}")

        items = self._items.get(installation_id, [])
        recent = list(reversed(items[-limit:]))

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "<channel>",
            f"<title>{html.escape(config.title)}</title>",
            f"<description>{html.escape(config.description)}</description>",
            f"<link>{html.escape(config.link)}</link>",
            f"<language>{html.escape(config.language)}</language>",
        ]

        for item in recent:
            lines.append("<item>")
            lines.append(f"<title>{html.escape(item.title)}</title>")
            lines.append(f"<description>{html.escape(item.description)}</description>")
            if item.link:
                lines.append(f"<link>{html.escape(item.link)}</link>")
            lines.append(f"<pubDate>{html.escape(item.date)}</pubDate>")
            lines.append(f'<guid isPermaLink="false">{html.escape(item.version)}</guid>')
            lines.append("</item>")

        lines.append("</channel>")
        lines.append("</rss>")
        return "\n".join(lines)

    def item_count(self, installation_id: str) -> int:
        return len(self._items.get(installation_id, []))
