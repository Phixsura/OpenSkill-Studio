"""API response cache — in-memory LRU cache with TTL for API responses."""
from __future__ import annotations
import time
from collections import OrderedDict


class ResponseCache:
    def __init__(self, *, max_size: int = 1000, default_ttl: int = 300):
        self._cache: OrderedDict[str, dict] = OrderedDict()
        self._max_size = max_size
        self._default_ttl = default_ttl
        self._hits = 0
        self._misses = 0

    def get(self, key: str, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        entry = self._cache.get(key)
        if entry and ts < entry["expires"]:
            self._hits += 1
            self._cache.move_to_end(key)
            return {"hit": True, "value": entry["value"]}
        if entry:
            del self._cache[key]
        self._misses += 1
        return {"hit": False}

    def set(self, key: str, value: dict, *, ttl: int | None = None,
            now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        ttl = ttl or self._default_ttl
        self._cache[key] = {"value": value, "expires": ts + ttl, "created": ts}
        self._cache.move_to_end(key)
        while len(self._cache) > self._max_size:
            self._cache.popitem(last=False)
        return {"cached": True, "key": key, "ttl": ttl}

    def invalidate(self, key: str) -> dict:
        if key in self._cache:
            del self._cache[key]
            return {"invalidated": True}
        return {"invalidated": False}

    def stats(self) -> dict:
        total = self._hits + self._misses
        hit_rate = round(self._hits / max(total, 1) * 100, 1)
        return {"size": len(self._cache), "max_size": self._max_size,
                "hits": self._hits, "misses": self._misses,
                "hit_rate": hit_rate, "hit_rate_display": f"{hit_rate}%"}
