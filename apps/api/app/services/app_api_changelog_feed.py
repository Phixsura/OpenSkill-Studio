"""App API Changelog Feed — paginated changelog feed.

Manages changelog feed:
- Add entries with version and date
- Paginated listing
- Filter by version range
- Per-installation scoped feeds
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FeedEntry:
    """A changelog feed entry."""

    entry_id: str
    version: str
    title: str
    summary: str
    published_at: float = field(default_factory=time.time)


class AppAPIChangelogFeed:
    """Paginated changelog feed."""

    def __init__(self) -> None:
        self._entries: dict[str, list[FeedEntry]] = {}

    def add_entry(
        self, installation_id: str, entry_id: str, version: str,
        title: str, summary: str,
    ) -> FeedEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not title:
            raise ValueError("title is required")

        entry = FeedEntry(
            entry_id=entry_id, version=version, title=title, summary=summary,
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def list_entries(
        self, installation_id: str, page: int = 1, page_size: int = 10,
    ) -> dict:
        entries = list(reversed(self._entries.get(installation_id, [])))
        total = len(entries)
        start = (page - 1) * page_size
        items = entries[start:start + page_size]
        return {
            "items": items,
            "total": total,
            "page": page,
            "pages": max(1, (total + page_size - 1) // page_size),
        }

    def by_version(self, installation_id: str, version: str) -> list[FeedEntry]:
        return [e for e in self._entries.get(installation_id, []) if e.version == version]

    def latest(self, installation_id: str) -> FeedEntry | None:
        entries = self._entries.get(installation_id, [])
        return entries[-1] if entries else None

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
