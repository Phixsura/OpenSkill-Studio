"""App Changelog Feed — structured changelog entries for marketplace app updates.

Provides a public-facing changelog feed for apps:
- Versioned changelog entries with categories (added, changed, fixed, removed, security)
- Markdown body support
- Version-to-version navigation
- RSS-ready data structure
- Breaking change flagging
- Search across changelog text
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()


class ChangeCategory(str, Enum):
    ADDED = "added"
    CHANGED = "changed"
    FIXED = "fixed"
    REMOVED = "removed"
    SECURITY = "security"
    DEPRECATED = "deprecated"


@dataclass
class ChangeItem:
    """A single change within a changelog entry."""

    category: ChangeCategory
    description: str
    breaking: bool = False


@dataclass
class ChangelogEntry:
    """A complete changelog entry for a version."""

    app_id: str
    version: str
    title: str
    items: list[ChangeItem]
    published_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    author: str = ""

    @property
    def has_breaking(self) -> bool:
        return any(i.breaking for i in self.items)

    @property
    def category_counts(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.items:
            counts[item.category.value] = counts.get(item.category.value, 0) + 1
        return counts

    def to_markdown(self) -> str:
        lines = [f"## {self.version} — {self.title}", ""]
        by_cat: dict[str, list[ChangeItem]] = {}
        for item in self.items:
            by_cat.setdefault(item.category.value, []).append(item)
        for cat in ChangeCategory:
            group = by_cat.get(cat.value, [])
            if group:
                lines.append(f"### {cat.value.title()}")
                for item in group:
                    prefix = "⚠️ **BREAKING:** " if item.breaking else ""
                    lines.append(f"- {prefix}{item.description}")
                lines.append("")
        return "\n".join(lines)


class AppChangelogFeed:
    """Manage and query changelog entries for apps."""

    def __init__(self):
        # (app_id, version) → ChangelogEntry
        self._entries: dict[tuple[str, str], ChangelogEntry] = {}
        # app_id → ordered list of versions (newest first)
        self._versions: dict[str, list[str]] = {}

    def publish(self, entry: ChangelogEntry) -> ChangelogEntry:
        """Publish a changelog entry."""
        if not entry.items:
            raise ValueError("Changelog entry must have at least one item")
        key = (entry.app_id, entry.version)
        self._entries[key] = entry
        versions = self._versions.setdefault(entry.app_id, [])
        if entry.version not in versions:
            versions.insert(0, entry.version)
        return entry

    def get(self, app_id: str, version: str) -> ChangelogEntry | None:
        return self._entries.get((app_id, version))

    def get_latest(self, app_id: str) -> ChangelogEntry | None:
        versions = self._versions.get(app_id, [])
        if not versions:
            return None
        return self._entries.get((app_id, versions[0]))

    def list_entries(self, app_id: str, limit: int = 20) -> list[ChangelogEntry]:
        versions = self._versions.get(app_id, [])
        return [self._entries[(app_id, v)] for v in versions[:limit]
                if (app_id, v) in self._entries]

    def search(self, app_id: str, query: str) -> list[ChangelogEntry]:
        """Search changelog text for a query string."""
        query_lower = query.lower()
        results = []
        for entry in self.list_entries(app_id, limit=1000):
            if query_lower in entry.title.lower():
                results.append(entry)
                continue
            if any(query_lower in item.description.lower() for item in entry.items):
                results.append(entry)
        return results

    def get_breaking_changes(self, app_id: str) -> list[ChangelogEntry]:
        """Get all entries that contain breaking changes."""
        return [e for e in self.list_entries(app_id, limit=1000) if e.has_breaking]

    def to_rss_items(self, app_id: str, limit: int = 10) -> list[dict]:
        """Generate RSS-ready item dicts."""
        entries = self.list_entries(app_id, limit=limit)
        return [
            {
                "title": f"{e.version}: {e.title}",
                "description": e.to_markdown(),
                "pubDate": e.published_at.isoformat(),
                "guid": f"{e.app_id}-{e.version}",
            }
            for e in entries
        ]
