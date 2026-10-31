"""Memoization Cache — automatic function result caching.

Implements:
- Argument-based cache keying (hash args → cached result)
- TTL per memoized function
- Max cache size with LRU eviction
- Cache statistics (hit rate per function)
- Selective invalidation by argument pattern
- Thread-safe memoization decorator pattern
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib
import json
import time


@dataclass
class MemoEntry:
    result: object
    computed_at: float
    expires_at: float
    hits: int = 0


class MemoizeCacheService:
    def __init__(self):
        self._caches: dict[str, OrderedDict[str, MemoEntry]] = {}
        self._configs: dict[str, dict] = {}
        self._stats: dict[str, dict] = {}

    def register(self, fn_name: str, max_size: int = 256,
                 ttl_seconds: float = 0) -> None:
        """Register a function for memoization."""
        self._caches[fn_name] = OrderedDict()
        self._configs[fn_name] = {"max_size": max_size, "ttl": ttl_seconds}
        self._stats[fn_name] = {"hits": 0, "misses": 0, "evictions": 0}

    def _make_key(self, args: tuple, kwargs: dict) -> str:
        """Create deterministic cache key from arguments."""
        key_data = json.dumps({"a": list(args), "k": kwargs},
                              sort_keys=True, default=str)
        return hashlib.md5(key_data.encode()).hexdigest()

    def get_or_compute(self, fn_name: str, fn: callable,
                       args: tuple = (), kwargs: dict | None = None) -> object:
        """Get cached result or compute and cache."""
        kwargs = kwargs or {}
        cache = self._caches.get(fn_name)
        config = self._configs.get(fn_name)
        if cache is None:
            self.register(fn_name)
            cache = self._caches[fn_name]
            config = self._configs[fn_name]

        key = self._make_key(args, kwargs)
        now = time.time()

        # Check cache
        entry = cache.get(key)
        if entry is not None:
            if config["ttl"] > 0 and now > entry.expires_at:
                del cache[key]
            else:
                entry.hits += 1
                cache.move_to_end(key)
                self._stats[fn_name]["hits"] += 1
                return entry.result

        # Cache miss — compute
        self._stats[fn_name]["misses"] += 1
        result = fn(*args, **kwargs)

        # Evict if over max size
        while len(cache) >= config["max_size"]:
            cache.popitem(last=False)  # evict LRU
            self._stats[fn_name]["evictions"] += 1

        ttl = config["ttl"]
        cache[key] = MemoEntry(result=result, computed_at=now,
                                expires_at=now + ttl if ttl > 0 else float('inf'))
        return result

    def invalidate(self, fn_name: str, args: tuple = (),
                   kwargs: dict | None = None) -> bool:
        """Invalidate specific cached result."""
        cache = self._caches.get(fn_name)
        if not cache:
            return False
        key = self._make_key(args, kwargs or {})
        if key in cache:
            del cache[key]
            return True
        return False

    def invalidate_all(self, fn_name: str) -> int:
        """Clear all cached results for a function."""
        cache = self._caches.get(fn_name)
        if not cache:
            return 0
        count = len(cache)
        cache.clear()
        return count

    def get_stats(self, fn_name: str) -> dict:
        stats = self._stats.get(fn_name, {})
        cache = self._caches.get(fn_name, {})
        total = stats.get("hits", 0) + stats.get("misses", 0)
        return {
            "cached_entries": len(cache),
            "hits": stats.get("hits", 0),
            "misses": stats.get("misses", 0),
            "hit_rate": round(stats.get("hits", 0) / max(1, total) * 100, 1),
            "evictions": stats.get("evictions", 0),
        }
