"""App Cache Manager — in-memory cache with TTL, LRU eviction, and namespacing.

Provides a caching layer for installed apps:
- Get/set/delete with TTL
- Namespace isolation per installation
- LRU eviction when max size exceeded
- Cache statistics (hits, misses, evictions)
- Bulk invalidation by prefix
"""

from __future__ import annotations

import time
from collections import OrderedDict
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class CacheEntry:
    """A cached value with metadata."""

    key: str
    value: object
    created_at: float
    expires_at: float | None
    access_count: int = 0


@dataclass
class CacheStats:
    """Cache statistics."""

    hits: int = 0
    misses: int = 0
    evictions: int = 0
    size: int = 0
    max_size: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.hits + self.misses
        return (self.hits / total * 100) if total > 0 else 0.0


class AppCacheManager:
    """In-memory cache with TTL and LRU eviction."""

    def __init__(self, max_size: int = 1000, default_ttl_seconds: float = 300) -> None:
        if max_size < 1:
            raise ValueError("max_size must be >= 1")
        if default_ttl_seconds <= 0:
            raise ValueError("default_ttl_seconds must be > 0")
        self._max_size = max_size
        self._default_ttl = default_ttl_seconds
        # (installation_id, key) → CacheEntry, ordered by access time
        self._store: OrderedDict[tuple[str, str], CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, installation_id: str, key: str, now: float | None = None) -> object | None:
        """Get a cached value. Returns None on miss or expiry."""
        now = now or time.time()
        compound = (installation_id, key)
        entry = self._store.get(compound)

        if entry is None:
            self._misses += 1
            return None

        # Check expiry
        if entry.expires_at and now >= entry.expires_at:
            del self._store[compound]
            self._misses += 1
            return None

        # Move to end (most recently used)
        self._store.move_to_end(compound)
        entry.access_count += 1
        self._hits += 1
        return entry.value

    def set(
        self,
        installation_id: str,
        key: str,
        value: object,
        ttl_seconds: float | None = None,
        now: float | None = None,
    ) -> CacheEntry:
        """Set a cached value with optional TTL."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key:
            raise ValueError("key is required")

        now = now or time.time()
        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        compound = (installation_id, key)

        # Remove old entry if exists
        if compound in self._store:
            del self._store[compound]

        # Evict LRU if at capacity
        while len(self._store) >= self._max_size:
            self._store.popitem(last=False)
            self._evictions += 1

        entry = CacheEntry(
            key=key,
            value=value,
            created_at=now,
            expires_at=now + ttl if ttl > 0 else None,
        )
        self._store[compound] = entry
        return entry

    def delete(self, installation_id: str, key: str) -> bool:
        """Delete a cached value. Returns True if found."""
        compound = (installation_id, key)
        if compound in self._store:
            del self._store[compound]
            return True
        return False

    def invalidate_prefix(self, installation_id: str, prefix: str) -> int:
        """Delete all keys matching a prefix. Returns count deleted."""
        to_delete = [
            k for k in self._store
            if k[0] == installation_id and k[1].startswith(prefix)
        ]
        for k in to_delete:
            del self._store[k]
        return len(to_delete)

    def exists(self, installation_id: str, key: str, now: float | None = None) -> bool:
        """Check if a key exists and is not expired."""
        return self.get(installation_id, key, now=now) is not None

    def get_stats(self) -> CacheStats:
        return CacheStats(
            hits=self._hits,
            misses=self._misses,
            evictions=self._evictions,
            size=len(self._store),
            max_size=self._max_size,
        )

    def clear(self, installation_id: str | None = None) -> int:
        """Clear cache entries. If installation_id given, only that namespace."""
        if installation_id is None:
            count = len(self._store)
            self._store.clear()
            return count
        to_delete = [k for k in self._store if k[0] == installation_id]
        for k in to_delete:
            del self._store[k]
        return len(to_delete)
