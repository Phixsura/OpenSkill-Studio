"""Cache Service — in-memory caching with TTL for marketplace data.

Provides a simple but effective cache layer for frequently accessed
marketplace data like extension listings, search results, and ratings.
"""
from __future__ import annotations
import time
from dataclasses import dataclass


@dataclass
class CacheEntry:
    key: str
    value: object
    created_at: float
    ttl_seconds: float
    hits: int = 0

    @property
    def expired(self) -> bool:
        return time.monotonic() - self.created_at > self.ttl_seconds


class CacheService:
    """In-memory cache with TTL, eviction, and hit tracking."""

    def __init__(self, default_ttl: float = 300.0, max_entries: int = 10000):
        self._cache: dict[str, CacheEntry] = {}
        self._default_ttl = default_ttl
        self._max_entries = max_entries
        self._total_hits = 0
        self._total_misses = 0

    def get(self, key: str) -> object | None:
        """Get a cached value. Returns None on miss or expiry."""
        entry = self._cache.get(key)
        if entry is None:
            self._total_misses += 1
            return None
        if entry.expired:
            del self._cache[key]
            self._total_misses += 1
            return None
        entry.hits += 1
        self._total_hits += 1
        return entry.value

    def set(self, key: str, value: object, ttl: float | None = None) -> None:
        """Set a cache entry with optional custom TTL."""
        if len(self._cache) >= self._max_entries:
            self._evict()
        self._cache[key] = CacheEntry(
            key=key, value=value,
            created_at=time.monotonic(),
            ttl_seconds=ttl if ttl is not None else self._default_ttl,
        )

    def delete(self, key: str) -> bool:
        return self._cache.pop(key, None) is not None

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        return count

    def has(self, key: str) -> bool:
        entry = self._cache.get(key)
        return entry is not None and not entry.expired

    def get_or_set(self, key: str, factory: callable, ttl: float | None = None) -> object:
        """Get from cache or compute and cache the value."""
        value = self.get(key)
        if value is not None:
            return value
        value = factory()
        self.set(key, value, ttl)
        return value

    def invalidate_prefix(self, prefix: str) -> int:
        """Invalidate all keys matching a prefix."""
        keys = [k for k in self._cache if k.startswith(prefix)]
        for k in keys:
            del self._cache[k]
        return len(keys)

    def _evict(self) -> None:
        """Evict expired entries, then LRU by hits."""
        # Remove expired first
        expired = [k for k, v in self._cache.items() if v.expired]
        for k in expired:
            del self._cache[k]
        # If still full, remove least-hit entry
        if len(self._cache) >= self._max_entries:
            lru_key = min(self._cache, key=lambda k: self._cache[k].hits)
            del self._cache[lru_key]

    def stats(self) -> dict:
        valid = sum(1 for e in self._cache.values() if not e.expired)
        return {
            "entries": len(self._cache),
            "valid": valid,
            "expired": len(self._cache) - valid,
            "hits": self._total_hits,
            "misses": self._total_misses,
            "hit_rate": round(self._total_hits / max(1, self._total_hits + self._total_misses), 4),
        }
