"""App Changelog Search — full-text search across changelog entries.

Provides search functionality for changelogs:
- Index entries by version, title, description
- Keyword search with relevance scoring
- Filter by version range
- Per-installation scoped search
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SearchEntry:
    """An indexed changelog entry."""

    entry_id: str
    version: str
    title: str
    description: str
    category: str = ""


@dataclass
class SearchResult:
    """A search result with relevance score."""

    entry: SearchEntry
    score: float
    matched_fields: list[str]


class AppChangelogSearch:
    """Full-text search across changelog entries."""

    def __init__(self) -> None:
        # installation_id → list[SearchEntry]
        self._entries: dict[str, list[SearchEntry]] = {}

    def index_entry(
        self,
        installation_id: str,
        entry_id: str,
        version: str,
        title: str,
        description: str,
        category: str = "",
    ) -> SearchEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not entry_id:
            raise ValueError("entry_id is required")

        entry = SearchEntry(
            entry_id=entry_id, version=version,
            title=title, description=description, category=category,
        )
        self._entries.setdefault(installation_id, []).append(entry)
        return entry

    def search(
        self,
        installation_id: str,
        query: str,
        version: str | None = None,
        category: str | None = None,
        limit: int = 20,
    ) -> list[SearchResult]:
        if not query:
            raise ValueError("query is required")

        entries = self._entries.get(installation_id, [])
        if version:
            entries = [e for e in entries if e.version == version]
        if category:
            entries = [e for e in entries if e.category == category]

        terms = query.lower().split()
        results: list[SearchResult] = []

        for entry in entries:
            score = 0.0
            matched: list[str] = []

            title_lower = entry.title.lower()
            desc_lower = entry.description.lower()

            for term in terms:
                if term in title_lower:
                    score += 3.0  # title matches weighted higher
                    if "title" not in matched:
                        matched.append("title")
                if term in desc_lower:
                    score += 1.0
                    if "description" not in matched:
                        matched.append("description")
                if term in entry.version.lower():
                    score += 2.0
                    if "version" not in matched:
                        matched.append("version")

            if score > 0:
                results.append(SearchResult(entry=entry, score=score, matched_fields=matched))

        results.sort(key=lambda r: r.score, reverse=True)
        return results[:limit]

    def entry_count(self, installation_id: str) -> int:
        return len(self._entries.get(installation_id, []))
