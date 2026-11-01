"""Endpoint Response Cache — LRU response cache with TTL and invalidation."""
from __future__ import annotations

import structlog
from collections import OrderedDict
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class CachedResponse:
    key: str
    body: dict | list | str
    status_code: int = 200
    created_at: float = 0.0
    ttl_seconds: float = 60.0
    hit_count: int = 0
    size_bytes: int = 0


@dataclass
class ResponseCache:
    """LRU response cache with TTL expiration."""

    _cache: OrderedDict[str, CachedResponse] = field(default_factory=OrderedDict)
    _max_entries: int = 1000
    _max_size_bytes: int = 50 * 1024 * 1024  # 50MB
    _total_hits: int = 0
    _total_misses: int = 0
    _current_size: int = 0

    def configure(self, max_entries: int = 1000, max_size_mb: int = 50) -> dict:
        if max_entries < 1:
            raise ValueError("max_entries must be positive")
        self._max_entries = max_entries
        self._max_size_bytes = max_size_mb * 1024 * 1024
        return {"max_entries": max_entries, "max_size_mb": max_size_mb}

    def put(self, key: str, body: dict | list | str, status_code: int = 200,
            ttl_seconds: float = 60.0, current_time: float = 0.0) -> dict:
        size = len(str(body))
        # Evict if at capacity
        while len(self._cache) >= self._max_entries:
            evicted_key, evicted = self._cache.popitem(last=False)
            self._current_size -= evicted.size_bytes
        entry = CachedResponse(key=key, body=body, status_code=status_code,
                                created_at=current_time, ttl_seconds=ttl_seconds,
                                size_bytes=size)
        if key in self._cache:
            self._current_size -= self._cache[key].size_bytes
        self._cache[key] = entry
        self._cache.move_to_end(key)
        self._current_size += size
        return {"key": key, "cached": True, "size_bytes": size}

    def get(self, key: str, current_time: float = 0.0) -> dict | None:
        entry = self._cache.get(key)
        if not entry:
            self._total_misses += 1
            return None
        # Check TTL
        if entry.ttl_seconds > 0 and (current_time - entry.created_at) > entry.ttl_seconds:
            self._cache.pop(key)
            self._current_size -= entry.size_bytes
            self._total_misses += 1
            return None
        entry.hit_count += 1
        self._total_hits += 1
        self._cache.move_to_end(key)
        return {"key": key, "body": entry.body, "status_code": entry.status_code,
                "hit_count": entry.hit_count, "age_seconds": current_time - entry.created_at}

    def invalidate(self, key: str) -> dict:
        entry = self._cache.pop(key, None)
        if entry:
            self._current_size -= entry.size_bytes
            return {"invalidated": True}
        return {"invalidated": False}

    def invalidate_pattern(self, prefix: str) -> dict:
        keys_to_remove = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_remove:
            self._current_size -= self._cache[k].size_bytes
            del self._cache[k]
        return {"invalidated": len(keys_to_remove)}

    def get_stats(self) -> dict:
        total = self._total_hits + self._total_misses
        hit_rate = round(self._total_hits / total * 100, 1) if total > 0 else 0
        return {
            "entries": len(self._cache),
            "max_entries": self._max_entries,
            "size_bytes": self._current_size,
            "total_hits": self._total_hits,
            "total_misses": self._total_misses,
            "hit_rate": hit_rate,
        }

    def clear(self) -> dict:
        count = len(self._cache)
        self._cache.clear()
        self._current_size = 0
        return {"cleared": count}
