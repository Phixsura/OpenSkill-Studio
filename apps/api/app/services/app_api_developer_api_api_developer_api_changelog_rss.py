"""App API Developer API Changelog RSS — generate RSS feeds for API changes."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
from xml.sax.saxutils import escape
import structlog

log = structlog.get_logger()

@dataclass
class RSSItem:
    item_id: str
    title: str
    description: str
    category: str  # "feature", "fix", "breaking", "deprecation"
    version: str
    published_at: float = field(default_factory=time.time)

class AppAPIDeveloperAPIApiDeveloperApiChangelogRss:
    def __init__(self) -> None:
        self._items: dict[str, list[RSSItem]] = {}

    def publish(self, installation_id: str, item_id: str, title: str, description: str, category: str, version: str) -> RSSItem:
        if not installation_id: raise ValueError("installation_id is required")
        if category not in ("feature", "fix", "breaking", "deprecation"): raise ValueError("invalid category")
        key = installation_id
        items = self._items.setdefault(key, [])
        if any(i.item_id == item_id for i in items): raise ValueError(f"Item {item_id} exists")
        item = RSSItem(item_id=item_id, title=title, description=description, category=category, version=version)
        items.append(item)
        return item

    def feed(self, installation_id: str, limit: int = 20) -> list[RSSItem]:
        return list(reversed(self._items.get(installation_id, [])[-limit:]))

    def by_category(self, installation_id: str, category: str) -> list[RSSItem]:
        return [i for i in self._items.get(installation_id, []) if i.category == category]

    def by_version(self, installation_id: str, version: str) -> list[RSSItem]:
        return [i for i in self._items.get(installation_id, []) if i.version == version]

    def render_xml(self, installation_id: str, title: str = "API Changelog") -> str:
        items = self.feed(installation_id)
        xml_items = "\n".join(f"<item><title>{escape(i.title)}</title><description>{escape(i.description)}</description><category>{escape(i.category)}</category></item>" for i in items)
        return f'<?xml version="1.0"?><rss version="2.0"><channel><title>{escape(title)}</title>{xml_items}</channel></rss>'
