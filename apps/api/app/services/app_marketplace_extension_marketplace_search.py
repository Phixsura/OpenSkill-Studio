"""Marketplace Search Engine — full-text search across extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
import re


@dataclass
class SearchableExt:
    extension_id: str
    name: str
    description: str
    tags: list[str] = field(default_factory=list)
    author: str = ""
    installs: int = 0
    rating: float = 0.0


class MarketplaceSearchService:
    def __init__(self):
        self._extensions: dict[str, SearchableExt] = {}

    def index(self, ext: SearchableExt) -> None:
        self._extensions[ext.extension_id] = ext

    def search(self, query: str, sort_by: str = "relevance",
               tag: str | None = None, min_rating: float = 0) -> list[SearchableExt]:
        q = query.lower().strip()
        results: list[tuple[float, SearchableExt]] = []

        for ext in self._extensions.values():
            if tag and tag not in ext.tags:
                continue
            if ext.rating < min_rating:
                continue

            score = 0.0
            name_lower = ext.name.lower()
            desc_lower = ext.description.lower()

            if q in name_lower:
                score += 10.0
                if name_lower.startswith(q):
                    score += 5.0
            if q in desc_lower:
                score += 3.0
            for t in ext.tags:
                if q in t.lower():
                    score += 2.0

            if score > 0:
                results.append((score, ext))

        if sort_by == "relevance":
            results.sort(key=lambda r: r[0], reverse=True)
        elif sort_by == "installs":
            results.sort(key=lambda r: r[1].installs, reverse=True)
        elif sort_by == "rating":
            results.sort(key=lambda r: r[1].rating, reverse=True)
        elif sort_by == "name":
            results.sort(key=lambda r: r[1].name.lower())

        return [r[1] for r in results]

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        p = prefix.lower()
        names = [e.name for e in self._extensions.values() if e.name.lower().startswith(p)]
        return sorted(names)[:limit]

    def get_popular(self, limit: int = 10) -> list[SearchableExt]:
        return sorted(self._extensions.values(), key=lambda e: e.installs, reverse=True)[:limit]
