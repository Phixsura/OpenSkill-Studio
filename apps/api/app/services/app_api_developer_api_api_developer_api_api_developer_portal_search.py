"""App API Developer Portal Search — search across documentation and endpoints."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SearchResult:
    result_id: str
    title: str
    content_preview: str
    result_type: str  # "endpoint", "documentation", "changelog", "guide"
    url: str
    relevance_score: float = 0.0

class AppAPIDeveloperAPIApiDeveloperApiApiDeveloperPortalSearch:
    def __init__(self) -> None:
        self._index: dict[str, list[SearchResult]] = {}
        self._query_count: dict[str, int] = {}

    def index(self, installation_id: str, result_id: str, title: str, content: str, result_type: str, url: str) -> SearchResult:
        if not installation_id: raise ValueError("installation_id is required")
        if result_type not in ("endpoint", "documentation", "changelog", "guide"): raise ValueError("invalid result_type")
        r = SearchResult(result_id=result_id, title=title, content_preview=content[:200], result_type=result_type, url=url)
        self._index.setdefault(installation_id, []).append(r)
        return r

    def search(self, installation_id: str, query: str, result_type: str | None = None, limit: int = 10) -> list[SearchResult]:
        if not query: return []
        self._query_count[installation_id] = self._query_count.get(installation_id, 0) + 1
        items = self._index.get(installation_id, [])
        q = query.lower()
        scored = []
        for item in items:
            if result_type and item.result_type != result_type: continue
            score = 0.0
            if q in item.title.lower(): score += 10.0
            if q in item.content_preview.lower(): score += 5.0
            if score > 0:
                item.relevance_score = score
                scored.append(item)
        return sorted(scored, key=lambda r: r.relevance_score, reverse=True)[:limit]

    def total_indexed(self, installation_id: str) -> int:
        return len(self._index.get(installation_id, []))

    def query_count(self, installation_id: str) -> int:
        return self._query_count.get(installation_id, 0)
