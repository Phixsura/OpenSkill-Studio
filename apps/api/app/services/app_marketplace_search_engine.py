"""Search Engine — full-text search across marketplace extensions and connectors.

Provides indexed search with relevance scoring, category filters,
tag matching, and sorting by popularity/rating/recency.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum


class SortBy(str, Enum):
    RELEVANCE = "relevance"
    POPULARITY = "popularity"
    RATING = "rating"
    RECENT = "recent"


@dataclass
class SearchableItem:
    item_id: str
    item_type: str  # "extension" or "connector"
    name: str
    description: str
    tags: list[str]
    category: str
    author: str
    downloads: int = 0
    rating: float = 0.0
    created_at: str = ""


class SearchEngine:
    """In-memory search engine with relevance scoring."""

    def __init__(self):
        self._items: dict[str, SearchableItem] = {}

    def index(self, item: SearchableItem) -> None:
        """Add or update an item in the search index."""
        self._items[item.item_id] = item

    def remove(self, item_id: str) -> bool:
        return self._items.pop(item_id, None) is not None

    def _score(self, item: SearchableItem, query: str) -> float:
        """Calculate relevance score for a query."""
        q = query.lower()
        score = 0.0
        # Name match (highest weight)
        if q in item.name.lower():
            score += 10.0
            if item.name.lower().startswith(q):
                score += 5.0
        # Description match
        if q in item.description.lower():
            score += 3.0
        # Tag match
        for tag in item.tags:
            if q in tag.lower():
                score += 4.0
        # Category match
        if q in item.category.lower():
            score += 2.0
        # Author match
        if q in item.author.lower():
            score += 1.0
        return score

    def search(
        self, query: str, item_type: str | None = None,
        category: str | None = None, tags: list[str] | None = None,
        sort_by: SortBy = SortBy.RELEVANCE, limit: int = 20,
    ) -> list[dict]:
        """Search with filters and sorting."""
        candidates = list(self._items.values())

        # Filters
        if item_type:
            candidates = [i for i in candidates if i.item_type == item_type]
        if category:
            candidates = [i for i in candidates if i.category == category]
        if tags:
            tag_set = set(t.lower() for t in tags)
            candidates = [i for i in candidates
                         if tag_set & set(t.lower() for t in i.tags)]

        # Score and filter by relevance
        scored = [(i, self._score(i, query)) for i in candidates]
        if query:
            scored = [(i, s) for i, s in scored if s > 0]

        # Sort
        if sort_by == SortBy.RELEVANCE:
            scored.sort(key=lambda x: x[1], reverse=True)
        elif sort_by == SortBy.POPULARITY:
            scored.sort(key=lambda x: x[0].downloads, reverse=True)
        elif sort_by == SortBy.RATING:
            scored.sort(key=lambda x: x[0].rating, reverse=True)
        elif sort_by == SortBy.RECENT:
            scored.sort(key=lambda x: x[0].created_at, reverse=True)

        return [
            {"item": i, "score": s}
            for i, s in scored[:limit]
        ]

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """Auto-suggest extension names based on prefix."""
        p = prefix.lower()
        names = [i.name for i in self._items.values() if i.name.lower().startswith(p)]
        return sorted(names)[:limit]

    def count(self, item_type: str | None = None) -> int:
        if item_type:
            return sum(1 for i in self._items.values() if i.item_type == item_type)
        return len(self._items)
