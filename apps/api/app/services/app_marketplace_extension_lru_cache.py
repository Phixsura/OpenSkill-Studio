"""LRU Cache with TTL — size-bounded cache with least-recently-used eviction.

Implements:
- O(1) get/put via dict + doubly-linked list (using OrderedDict)
- Per-entry TTL with lazy expiration
- Size limit with LRU eviction
- Hit/miss/eviction statistics
- Bulk invalidation by prefix
"""
from __future__ import annotations
from collections import OrderedDict
from dataclasses import dataclass
import time


@dataclass
class CacheEntry:
    value: object
    expires_at: float
    size_bytes: int = 0
    created_at: float = 0.0
    access_count: int = 0


class LruCacheWithTtlService:
    def __init__(self, max_entries: int = 1000, max_size_bytes: int = 0,
                 default_ttl: float = 3600):
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._max_entries = max_entries
        self._max_size_bytes = max_size_bytes  # 0 = unlimited
        self._default_ttl = default_ttl
        self._current_size = 0
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> object | None:
        entry = self._cache.get(key)
        if entry is None:
            self._misses += 1
            return None

        # Check TTL
        if entry.expires_at != 0 and time.time() > entry.expires_at:
            self._remove(key)
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._cache.move_to_end(key)
        entry.access_count += 1
        self._hits += 1
        return entry.value

    def put(self, key: str, value: object, ttl: float = 0,
            size_bytes: int = 0) -> None:
        ttl = ttl or self._default_ttl
        now = time.time()
        expires = now + ttl if ttl > 0 else 0

        # Update existing
        if key in self._cache:
            old = self._cache[key]
            self._current_size -= old.size_bytes
            self._cache.move_to_end(key)
            self._cache[key] = CacheEntry(value=value, expires_at=expires,
                                          size_bytes=size_bytes, created_at=now)
            self._current_size += size_bytes
            return

        # Evict if needed
        self._evict_expired()
        while len(self._cache) >= self._max_entries:
            self._evict_lru()
        if self._max_size_bytes > 0:
            while self._current_size + size_bytes > self._max_size_bytes and self._cache:
                self._evict_lru()

        self._cache[key] = CacheEntry(value=value, expires_at=expires,
                                      size_bytes=size_bytes, created_at=now)
        self._current_size += size_bytes

    def delete(self, key: str) -> bool:
        if key in self._cache:
            self._remove(key)
            return True
        return False

    def invalidate_prefix(self, prefix: str) -> int:
        keys = [k for k in self._cache if k.startswith(prefix)]
        for k in keys:
            self._remove(k)
        return len(keys)

    def _remove(self, key: str) -> None:
        entry = self._cache.pop(key, None)
        if entry:
            self._current_size -= entry.size_bytes

    def _evict_lru(self) -> None:
        if self._cache:
            key, entry = self._cache.popitem(last=False)
            self._current_size -= entry.size_bytes
            self._evictions += 1

    def _evict_expired(self) -> int:
        now = time.time()
        expired = [k for k, v in self._cache.items()
                   if v.expires_at != 0 and v.expires_at < now]
        for k in expired:
            self._remove(k)
            self._evictions += 1
        return len(expired)

    def stats(self) -> dict:
        total = self._hits + self._misses
        return {
            "entries": len(self._cache),
            "size_bytes": self._current_size,
            "max_entries": self._max_entries,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": round(self._hits / total * 100, 1) if total else 0,
            "evictions": self._evictions,
        }

    def clear(self) -> int:
        count = len(self._cache)
        self._cache.clear()
        self._current_size = 0
        return count
