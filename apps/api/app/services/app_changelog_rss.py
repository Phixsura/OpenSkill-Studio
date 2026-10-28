"""App Changelog RSS — generate RSS feeds from changelog entries.

Generates RSS feeds:
- Build RSS XML from changelog entries
- HTML entity escaping for security
- Configurable feed metadata
- Per-installation scoped feeds
"""

from __future__ import annotations

import html
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ChangelogItem:
    """A changelog entry for RSS."""

    item_id: str
    title: str
    description: str
    version: str
    published_at: float = field(default_factory=time.time)


@dataclass
class FeedConfig:
    """RSS feed configuration."""

    title: str
    link: str
    description: str
    language: str = "en"


class AppChangelogRSS:
    """Generate RSS feeds from changelog entries."""

    def __init__(self) -> None:
        self._items: dict[str, list[ChangelogItem]] = {}
        self._configs: dict[str, FeedConfig] = {}

    def configure(
        self, installation_id: str, title: str, link: str,
        description: str, language: str = "en",
    ) -> FeedConfig:
        if not installation_id:
            raise ValueError("installation_id is required")
        config = FeedConfig(title=title, link=link, description=description, language=language)
        self._configs[installation_id] = config
        return config

    def add_item(
        self, installation_id: str, item_id: str, title: str,
        description: str, version: str,
    ) -> ChangelogItem:
        if not installation_id:
            raise ValueError("installation_id is required")
        item = ChangelogItem(
            item_id=item_id, title=title,
            description=description, version=version,
        )
        self._items.setdefault(installation_id, []).append(item)
        return item

    def generate_rss(self, installation_id: str, limit: int = 20) -> str:
        """Generate RSS 2.0 XML feed. All text is HTML-escaped."""
        config = self._configs.get(installation_id)
        if config is None:
            raise ValueError("Feed not configured")

        items = list(reversed(self._items.get(installation_id, [])[-limit:]))

        lines = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            '<rss version="2.0">',
            "<channel>",
            f"<title>{html.escape(config.title)}</title>",
            f"<link>{html.escape(config.link)}</link>",
            f"<description>{html.escape(config.description)}</description>",
            f"<language>{html.escape(config.language)}</language>",
        ]

        for item in items:
            lines.extend([
                "<item>",
                f"<title>{html.escape(item.title)}</title>",
                f"<description>{html.escape(item.description)}</description>",
                f"<guid>{html.escape(item.item_id)}</guid>",
                "</item>",
            ])

        lines.extend(["</channel>", "</rss>"])
        return "\n".join(lines)

    def item_count(self, installation_id: str) -> int:
        return len(self._items.get(installation_id, []))
