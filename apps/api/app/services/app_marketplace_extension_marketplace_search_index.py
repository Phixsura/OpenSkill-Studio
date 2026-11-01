"""Search Index — full-text search index management for the marketplace.

Manages tokenization, indexing, and ranked retrieval for extension
search with support for boosted fields, facets, and spelling suggestions.
"""
from __future__ import annotations
import re
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class IndexedDocument:
    doc_id: str
    fields: dict[str, str]  # field_name -> text
    boost: float = 1.0


class SearchIndex:
    """Full-text search index with field boosting and facets."""

    FIELD_BOOSTS = {"name": 10.0, "tags": 5.0, "description": 2.0, "author": 1.5, "category": 1.0}
    STOP_WORDS = {"the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to", "for", "of", "and", "or"}

    def __init__(self):
        self._docs: dict[str, IndexedDocument] = {}
        self._inverted: dict[str, dict[str, float]] = defaultdict(dict)  # token -> {doc_id: score}
        self._facets: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    def _tokenize(self, text: str) -> list[str]:
        tokens = re.findall(r'[a-z0-9]+', text.lower())
        return [t for t in tokens if t not in self.STOP_WORDS and len(t) > 1]

    def index(self, doc: IndexedDocument) -> None:
        """Index a document."""
        self._docs[doc.doc_id] = doc
        for field_name, text in doc.fields.items():
            boost = self.FIELD_BOOSTS.get(field_name, 1.0) * doc.boost
            tokens = self._tokenize(text)
            for token in tokens:
                self._inverted[token][doc.doc_id] = self._inverted[token].get(doc.doc_id, 0) + boost
            # Track facets for category
            if field_name == "category":
                self._facets["category"][text] += 1

    def remove(self, doc_id: str) -> bool:
        if doc_id not in self._docs:
            return False
        doc = self._docs.pop(doc_id)
        for field_name, text in doc.fields.items():
            for token in self._tokenize(text):
                self._inverted[token].pop(doc_id, None)
        return True

    def search(self, query: str, limit: int = 20, category: str | None = None) -> list[dict]:
        """Search with ranked results."""
        tokens = self._tokenize(query)
        if not tokens:
            return []

        scores: dict[str, float] = defaultdict(float)
        for token in tokens:
            for doc_id, score in self._inverted.get(token, {}).items():
                scores[doc_id] += score

        results = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if category:
            results = [(did, s) for did, s in results if self._docs.get(did, IndexedDocument("", {})).fields.get("category") == category]

        return [
            {"doc_id": did, "score": round(score, 2), "fields": self._docs[did].fields}
            for did, score in results[:limit]
            if did in self._docs
        ]

    def suggest(self, prefix: str, limit: int = 5) -> list[str]:
        """Suggest completions from indexed tokens."""
        p = prefix.lower()
        return sorted([t for t in self._inverted if t.startswith(p)],
                       key=lambda t: sum(self._inverted[t].values()), reverse=True)[:limit]

    def get_facets(self) -> dict[str, dict[str, int]]:
        return dict(self._facets)

    def doc_count(self) -> int:
        return len(self._docs)
