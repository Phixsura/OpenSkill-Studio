"""Capped Collection — fixed-size collection with automatic eviction.

MongoDB-style: oldest documents automatically removed when cap reached.
Natural FIFO ordering, no manual deletion needed.

Implements:
- Insert with automatic eviction at capacity
- Size cap (max documents) and byte cap (max total bytes)
- Natural ordering (insertion order preserved)
- Tailable cursor (read new documents as they arrive)
- No update/delete (append-only by design)
- Bulk insert
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Document:
    doc_id: str
    data: dict
    size_bytes: int = 0
    inserted_at: float = 0.0
    def __post_init__(self):
        if not self.inserted_at: self.inserted_at = time.time()
        if not self.size_bytes:
            import json
            self.size_bytes = len(json.dumps(self.data))


class CappedCollectionService:
    def __init__(self, max_docs: int = 10000, max_bytes: int = 0):
        self._docs: list[Document] = []
        self._max_docs = max_docs
        self._max_bytes = max_bytes  # 0 = no byte limit
        self._current_bytes = 0
        self._total_inserted = 0
        self._total_evicted = 0
        self._counter = 0
        self._cursor_positions: dict[str, int] = {}  # cursor_id → position

    def insert(self, data: dict) -> Document:
        """Insert a document. Evicts oldest if at capacity."""
        self._counter += 1
        doc = Document(doc_id=f"doc-{self._counter}", data=data)
        self._current_bytes += doc.size_bytes

        # Evict by document count
        while len(self._docs) >= self._max_docs:
            self._evict_oldest()

        # Evict by byte limit
        if self._max_bytes > 0:
            while self._current_bytes > self._max_bytes and self._docs:
                self._evict_oldest()

        self._docs.append(doc)
        self._total_inserted += 1
        return doc

    def insert_many(self, items: list[dict]) -> int:
        """Bulk insert. Returns count inserted."""
        for data in items:
            self.insert(data)
        return len(items)

    def _evict_oldest(self) -> None:
        if self._docs:
            evicted = self._docs.pop(0)
            self._current_bytes -= evicted.size_bytes
            self._total_evicted += 1

    def find(self, limit: int = 100, skip: int = 0) -> list[Document]:
        """Query documents in insertion order."""
        return self._docs[skip:skip + limit]

    def find_latest(self, n: int = 10) -> list[Document]:
        """Get the N most recent documents."""
        return list(reversed(self._docs[-n:]))

    def tail(self, cursor_id: str, batch_size: int = 10) -> list[Document]:
        """Tailable cursor: get new documents since last read."""
        pos = self._cursor_positions.get(cursor_id, 0)
        docs = self._docs[pos:pos + batch_size]
        self._cursor_positions[cursor_id] = pos + len(docs)
        return docs

    def count(self) -> int:
        return len(self._docs)

    def stats(self) -> dict:
        return {
            "count": len(self._docs),
            "max_docs": self._max_docs,
            "current_bytes": self._current_bytes,
            "max_bytes": self._max_bytes,
            "total_inserted": self._total_inserted,
            "total_evicted": self._total_evicted,
            "utilization_pct": round(len(self._docs) / max(1, self._max_docs) * 100, 1),
        }
