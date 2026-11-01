"""Extension Search Index — full-text search for marketplace extensions.

Indexes extensions with tokenization, TF-IDF-like scoring, faceted
filtering by category/tags/rating, and autocomplete suggestions.
"""
from __future__ import annotations
import re
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class SearchDoc:
    extension_id: str
    name: str
    description: str
    category: str
    tags: list[str] = field(default_factory=list)
    rating: float = 0.0
    installs: int = 0
    tokens: list[str] = field(default_factory=list)


class ExtensionSearchIndexService:
    """Full-text search index for marketplace extensions."""

    def __init__(self):
        self._docs: dict[str, SearchDoc] = {}
        self._inverted: dict[str, set[str]] = defaultdict(set)

    def _tokenize(self, text: str) -> list[str]:
        return [t.lower() for t in re.findall(r'\w+', text) if len(t) >= 2]

    def index(self, extension_id: str, name: str, description: str,
              category: str, tags: list[str] | None = None,
              rating: float = 0.0, installs: int = 0) -> SearchDoc:
        tokens = self._tokenize(f"{name} {description} {category} {' '.join(tags or [])}")
        doc = SearchDoc(
            extension_id=extension_id, name=name, description=description,
            category=category, tags=tags or [], rating=rating,
            installs=installs, tokens=tokens,
        )
        self._docs[extension_id] = doc
        for token in set(tokens):
            self._inverted[token].add(extension_id)
        return doc

    def search(self, query: str, category: str | None = None,
               min_rating: float = 0, sort_by: str = "relevance",
               limit: int = 20) -> list[SearchDoc]:
        tokens = self._tokenize(query)
        if not tokens:
            return []

        # Score by token matches
        scores: dict[str, float] = defaultdict(float)
        for token in tokens:
            for ext_id in self._inverted.get(token, set()):
                doc = self._docs[ext_id]
                # Boost name matches
                name_tokens = self._tokenize(doc.name)
                if token in name_tokens:
                    scores[ext_id] += 3.0
                else:
                    scores[ext_id] += 1.0

        # Filter
        results = []
        for ext_id, score in scores.items():
            doc = self._docs[ext_id]
            if category and doc.category != category:
                continue
            if doc.rating < min_rating:
                continue
            results.append((score, doc))

        # Sort
        if sort_by == "rating":
            results.sort(key=lambda x: x[1].rating, reverse=True)
        elif sort_by == "installs":
            results.sort(key=lambda x: x[1].installs, reverse=True)
        else:
            results.sort(key=lambda x: x[0], reverse=True)

        return [doc for _, doc in results[:limit]]

    def autocomplete(self, prefix: str, limit: int = 10) -> list[str]:
        prefix_lower = prefix.lower()
        matches = set()
        for doc in self._docs.values():
            if prefix_lower in doc.name.lower():
                matches.add(doc.name)
        return sorted(matches)[:limit]

    def get_facets(self) -> dict:
        categories: dict[str, int] = defaultdict(int)
        tags: dict[str, int] = defaultdict(int)
        for doc in self._docs.values():
            categories[doc.category] += 1
            for t in doc.tags:
                tags[t] += 1
        return {"categories": dict(categories),
                "tags": dict(sorted(tags.items(), key=lambda x: -x[1])[:20])}
