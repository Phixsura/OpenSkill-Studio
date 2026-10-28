"""App API Changelog Search — full-text search across changelog entries.

Manages changelog search:
- Index entries for search
- Search by keyword across title and content
- Rank results by relevance
- Per-installation scoped search
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SearchableEntry:
    """A searchable changelog entry."""

    entry_id: str
    title: str
    content: str
    version: str
    tags: list[str] = field(default_factory=list)


@dataclass
class SearchResult:
    """A search result with score."""

    entry: SearchableEntry
    score: float


class AppAPIChangelogSearch:
    """Full-text search across changelog entries."""

    def __init__(self) -> None:
        self._entries: dict[str, list[SearchableEntry]] = {}

    def index(
        self, installation_id: str, entry_id: str, title: str,
        content: str, version: str, tags: list[str] | None = None,
    ) -> SearchableEntry:
        if not installation_id:
            raise ValueError("installation_id is required")

        entry = SearchableEntry(
            entry_id=entry_id, title=title, content=content,
            version=version, tags=tags or [],
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def search(self, installation_id: str, query: str, limit: int = 10) -> list[SearchResult]:
        if not query.strip():
            return []
        q = query.lower()
        results: list[SearchResult] = []

        for entry in self._entries.get(installation_id, []):
            score = 0.0
            title_lower = entry.title.lower()
            content_lower = entry.content.lower()
            # Title match worth more
            if q in title_lower:
                score += 10.0
            if q in content_lower:
                score += 5.0
            # Tag match
            for tag in entry.tags:
                if q in tag.lower():
                    score += 3.0
            if score > 0:
                results.append(SearchResult(entry=entry, score=score))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
