"""Consumer API Changelog RSS — generate RSS feeds for API changes."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from html import escape
import structlog

log = structlog.get_logger()

@dataclass
class ChangelogItem:
    item_id: str
    title: str
    description: str
    version: str
    change_type: str  # "feature", "fix", "breaking", "deprecation"
    published_at: datetime
    author: str = ""

@dataclass
class RSSFeed:
    title: str
    description: str
    items: list[ChangelogItem]
    last_updated: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiChangelogRss:
    def __init__(self) -> None:
        self._items: dict[tuple[str, str], ChangelogItem] = {}

    def add_item(self, installation_id: str, item: ChangelogItem) -> ChangelogItem:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not item.title:
            raise ValueError("title is required")
        if item.change_type not in ("feature", "fix", "breaking", "deprecation", "security"):
            raise ValueError(f"Invalid change_type: {item.change_type}")
        self._items[(installation_id, item.item_id)] = item
        return item

    def generate_feed(self, installation_id: str, title: str = "API Changelog", limit: int = 20) -> RSSFeed:
        items = sorted([i for (inst, _), i in self._items.items() if inst == installation_id], key=lambda i: i.published_at, reverse=True)[:limit]
        last_updated = items[0].published_at if items else None
        return RSSFeed(title=title, description=f"Latest changes for {title}", items=items, last_updated=last_updated)

    def render_xml(self, installation_id: str, base_url: str = "https://api.example.com", limit: int = 20) -> str:
        feed = self.generate_feed(installation_id, limit=limit)
        xml_items = []
        for item in feed.items:
            xml_items.append(f"<item><title>{escape(item.title)}</title><description>{escape(item.description)}</description><pubDate>{item.published_at.isoformat()}</pubDate><guid>{escape(item.item_id)}</guid></item>")
        return f'<?xml version="1.0"?><rss version="2.0"><channel><title>{escape(feed.title)}</title><link>{escape(base_url)}</link><description>{escape(feed.description)}</description>{"".join(xml_items)}</channel></rss>'

    def get_item(self, installation_id: str, item_id: str) -> ChangelogItem | None:
        return self._items.get((installation_id, item_id))

    def list_items(self, installation_id: str, change_type: str | None = None) -> list[ChangelogItem]:
        items = [i for (inst, _), i in self._items.items() if inst == installation_id]
        if change_type:
            items = [i for i in items if i.change_type == change_type]
        return sorted(items, key=lambda i: i.published_at, reverse=True)
