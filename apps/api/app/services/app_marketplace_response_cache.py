"""Response Cache — HTTP response caching for extension API endpoints.

Implements cache-control semantics with ETags, conditional requests,
cache invalidation by tags, and stale-while-revalidate support.
"""
from __future__ import annotations
import hashlib
import time
from dataclasses import dataclass, field


@dataclass
class CachedResponse:
    key: str
    body: bytes
    content_type: str
    etag: str
    max_age: int
    created_at: float
    tags: list[str] = field(default_factory=list)
    stale_while_revalidate: int = 0

    @property
    def age(self) -> int:
        return int(time.monotonic() - self.created_at)

    @property
    def is_fresh(self) -> bool:
        return self.age <= self.max_age

    @property
    def is_stale_ok(self) -> bool:
        return self.age <= self.max_age + self.stale_while_revalidate


class ResponseCache:
    """HTTP response cache with ETags and tag-based invalidation."""

    def __init__(self, max_entries: int = 5000):
        self._cache: dict[str, CachedResponse] = {}
        self._max_entries = max_entries

    def _generate_etag(self, body: bytes) -> str:
        return f'"{hashlib.md5(body).hexdigest()[:16]}"'

    def put(self, key: str, body: bytes, content_type: str = "application/json",
            max_age: int = 300, tags: list[str] | None = None,
            stale_while_revalidate: int = 0) -> CachedResponse:
        """Cache a response."""
        if len(self._cache) >= self._max_entries:
            self._evict_expired()
        etag = self._generate_etag(body)
        entry = CachedResponse(
            key=key, body=body, content_type=content_type,
            etag=etag, max_age=max_age, created_at=time.monotonic(),
            tags=tags or [], stale_while_revalidate=stale_while_revalidate,
        )
        self._cache[key] = entry
        return entry

    def get(self, key: str, if_none_match: str = "") -> tuple[CachedResponse | None, str]:
        """Get cached response. Returns (entry, status: 'hit'|'stale'|'miss'|'not_modified')."""
        entry = self._cache.get(key)
        if not entry:
            return None, "miss"

        # ETag conditional check
        if if_none_match and if_none_match == entry.etag:
            return entry, "not_modified"

        if entry.is_fresh:
            return entry, "hit"

        if entry.is_stale_ok:
            return entry, "stale"

        # Expired beyond stale window
        del self._cache[key]
        return None, "miss"

    def invalidate(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def invalidate_by_tag(self, tag: str) -> int:
        """Invalidate all entries matching a tag."""
        keys = [k for k, v in self._cache.items() if tag in v.tags]
        for k in keys:
            del self._cache[k]
        return len(keys)

    def get_cache_headers(self, entry: CachedResponse) -> dict[str, str]:
        """Generate HTTP cache headers for a response."""
        headers = {
            "ETag": entry.etag,
            "Cache-Control": f"max-age={entry.max_age}",
            "Age": str(entry.age),
            "Content-Type": entry.content_type,
        }
        if entry.stale_while_revalidate:
            headers["Cache-Control"] += f", stale-while-revalidate={entry.stale_while_revalidate}"
        return headers

    def stats(self) -> dict:
        now = time.monotonic()
        entries = list(self._cache.values())
        fresh = sum(1 for e in entries if e.is_fresh)
        return {
            "total": len(entries), "fresh": fresh,
            "stale": len(entries) - fresh,
            "max_entries": self._max_entries,
        }

    def _evict_expired(self) -> None:
        expired = [k for k, v in self._cache.items() if not v.is_stale_ok]
        for k in expired:
            del self._cache[k]
