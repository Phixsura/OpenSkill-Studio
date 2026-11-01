"""App Search Index — full-text search over app resources.

Manages search indexes for installed apps:
- Index documents with fields
- Keyword search with term matching
- Faceted results by field
- Per-installation scoped indexes
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class IndexedDocument:
    """A document in the search index."""

    doc_id: str
    doc_type: str
    fields: dict[str, str]


@dataclass
class SearchHit:
    """A search result."""

    doc: IndexedDocument
    score: float
    matched_fields: list[str]


class AppSearchIndex:
    """Full-text search over app resources."""

    def __init__(self) -> None:
        # installation_id → list[IndexedDocument]
        self._docs: dict[str, list[IndexedDocument]] = {}

    def index_document(
        self,
        installation_id: str,
        doc_id: str,
        doc_type: str,
        fields: dict[str, str],
    ) -> IndexedDocument:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not doc_id:
            raise ValueError("doc_id is required")

        doc = IndexedDocument(doc_id=doc_id, doc_type=doc_type, fields=fields)
        docs = self._docs.setdefault(installation_id, [])
        # Replace if exists
        docs[:] = [d for d in docs if d.doc_id != doc_id]
        docs.append(doc)
        return doc

    def search(
        self,
        installation_id: str,
        query: str,
        doc_type: str | None = None,
        limit: int = 20,
    ) -> list[SearchHit]:
        if not query:
            raise ValueError("query is required")

        docs = self._docs.get(installation_id, [])
        if doc_type:
            docs = [d for d in docs if d.doc_type == doc_type]

        terms = query.lower().split()
        hits: list[SearchHit] = []

        for doc in docs:
            score = 0.0
            matched: list[str] = []
            for fname, fval in doc.fields.items():
                val_lower = fval.lower()
                for term in terms:
                    if term in val_lower:
                        score += 1.0
                        if fname not in matched:
                            matched.append(fname)
            if score > 0:
                hits.append(SearchHit(doc=doc, score=score, matched_fields=matched))

        hits.sort(key=lambda h: h.score, reverse=True)
        return hits[:limit]

    def remove_document(self, installation_id: str, doc_id: str) -> bool:
        docs = self._docs.get(installation_id, [])
        before = len(docs)
        self._docs[installation_id] = [d for d in docs if d.doc_id != doc_id]
        return len(self._docs[installation_id]) < before

    def doc_count(self, installation_id: str) -> int:
        return len(self._docs.get(installation_id, []))

    def facets(self, installation_id: str, field_name: str) -> dict[str, int]:
        """Count documents by a field value."""
        counts: dict[str, int] = {}
        for doc in self._docs.get(installation_id, []):
            val = doc.fields.get(field_name, "")
            if val:
                counts[val] = counts.get(val, 0) + 1
        return counts
