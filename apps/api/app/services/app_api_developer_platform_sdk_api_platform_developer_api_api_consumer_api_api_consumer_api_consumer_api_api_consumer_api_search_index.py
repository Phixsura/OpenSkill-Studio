"""Consumer API Search Index — full-text search across API resources."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SearchDocument:
    doc_id: str
    doc_type: str  # "endpoint", "webhook", "changelog", "doc"
    title: str
    content: str
    url: str = ""
    tags: list[str] = field(default_factory=list)

@dataclass
class SearchResult:
    doc_id: str
    doc_type: str
    title: str
    snippet: str
    score: float
    url: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiConsumerApiSearchIndex:
    def __init__(self) -> None:
        self._docs: dict[tuple[str, str], SearchDocument] = {}

    def index(self, installation_id: str, doc: SearchDocument) -> SearchDocument:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not doc.title and not doc.content:
            raise ValueError("Document must have title or content")
        self._docs[(installation_id, doc.doc_id)] = doc
        return doc

    def remove(self, installation_id: str, doc_id: str) -> None:
        key = (installation_id, doc_id)
        if key not in self._docs:
            raise ValueError("Document not found")
        del self._docs[key]

    def search(self, installation_id: str, query: str, doc_type: str | None = None, limit: int = 10) -> list[SearchResult]:
        q = query.lower()
        tokens = q.split()
        results: list[SearchResult] = []
        for (inst, _), doc in self._docs.items():
            if inst != installation_id:
                continue
            if doc_type and doc.doc_type != doc_type:
                continue
            text = f"{doc.title} {doc.content}".lower()
            score = sum(1 for t in tokens if t in text)
            if score == 0:
                continue
            # Extract snippet
            idx = text.find(tokens[0])
            start = max(0, idx - 30)
            snippet = text[start:start + 100].strip()
            results.append(SearchResult(doc_id=doc.doc_id, doc_type=doc.doc_type, title=doc.title, snippet=snippet, score=score, url=doc.url))
        return sorted(results, key=lambda r: -r.score)[:limit]

    def count(self, installation_id: str) -> dict[str, int]:
        counts: dict[str, int] = {}
        for (inst, _), doc in self._docs.items():
            if inst == installation_id:
                counts[doc.doc_type] = counts.get(doc.doc_type, 0) + 1
        return counts
