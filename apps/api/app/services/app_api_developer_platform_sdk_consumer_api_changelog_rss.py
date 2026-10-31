"""Consumer API Changelog RSS — RSS/Atom feed generation for changelogs."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field
from datetime import datetime, timezone

logger = structlog.get_logger()


@dataclass
class FeedEntry:
    entry_id: str
    title: str
    content: str
    version: str
    published_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    category: str = "update"  # update, feature, bugfix, security, breaking
    link: str = ""


@dataclass
class ChangelogFeed:
    """Generate RSS/Atom feeds for API changelogs."""

    _entries: list[FeedEntry] = field(default_factory=list)
    _feed_title: str = "API Changelog"
    _feed_url: str = ""

    def configure(self, title: str, url: str = "") -> dict:
        self._feed_title = title
        self._feed_url = url
        return {"title": title, "url": url}

    def add_entry(self, entry: FeedEntry) -> dict:
        if any(e.entry_id == entry.entry_id for e in self._entries):
            raise ValueError(f"Entry {entry.entry_id} already exists")
        if not entry.title:
            raise ValueError("Title is required")
        self._entries.append(entry)
        self._entries.sort(key=lambda e: e.published_at, reverse=True)
        logger.info("feed_entry_added", entry_id=entry.entry_id)
        return {"entry_id": entry.entry_id, "title": entry.title}

    def generate_rss(self, limit: int = 20) -> str:
        entries = self._entries[:limit]
        items = []
        for e in entries:
            items.append(
                f"  <item>\n"
                f"    <title>{e.title}</title>\n"
                f"    <description>{e.content}</description>\n"
                f"    <guid>{e.entry_id}</guid>\n"
                f"    <pubDate>{e.published_at}</pubDate>\n"
                f"    <category>{e.category}</category>\n"
                f"  </item>"
            )
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<rss version="2.0">\n'
            f'<channel>\n'
            f'  <title>{self._feed_title}</title>\n'
            f'  <link>{self._feed_url}</link>\n'
            f'{"".join(items)}\n'
            f'</channel>\n'
            f'</rss>'
        )

    def generate_atom(self, limit: int = 20) -> str:
        entries = self._entries[:limit]
        items = []
        for e in entries:
            items.append(
                f"  <entry>\n"
                f"    <title>{e.title}</title>\n"
                f"    <id>{e.entry_id}</id>\n"
                f"    <updated>{e.published_at}</updated>\n"
                f"    <content>{e.content}</content>\n"
                f"    <category term=\"{e.category}\"/>\n"
                f"  </entry>"
            )
        return (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<feed xmlns="http://www.w3.org/2005/Atom">\n'
            f'  <title>{self._feed_title}</title>\n'
            f'{"".join(items)}\n'
            f'</feed>'
        )

    def get_entries(self, category: str | None = None, limit: int = 20) -> list[dict]:
        entries = self._entries
        if category:
            entries = [e for e in entries if e.category == category]
        return [
            {"entry_id": e.entry_id, "title": e.title, "version": e.version,
             "category": e.category, "published_at": e.published_at}
            for e in entries[:limit]
        ]

    def get_stats(self) -> dict:
        by_cat: dict[str, int] = {}
        for e in self._entries:
            by_cat[e.category] = by_cat.get(e.category, 0) + 1
        return {
            "total_entries": len(self._entries),
            "by_category": by_cat,
            "feed_title": self._feed_title,
        }
