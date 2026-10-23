from __future__ import annotations
"""Cache manager — in-memory LRU cache with TTL and stats."""

import time
from collections import OrderedDict


class CacheManager:
    def __init__(self, *, max_size: int = 100, ttl_s: float = 300):
        self._cache: OrderedDict[str, tuple[float, object]] = OrderedDict()
        self.max_size = max_size
        self.ttl_s = ttl_s
        self.hits = 0
        self.misses = 0

    def get(self, key: str, now: float | None = None) -> object | None:
        t = now if now is not None else time.monotonic()
        if key in self._cache:
            ts, val = self._cache[key]
            if t - ts < self.ttl_s:
                self._cache.move_to_end(key)
                self.hits += 1
                return val
            del self._cache[key]
        self.misses += 1
        return None

    def set(self, key: str, value: object, now: float | None = None) -> None:
        t = now if now is not None else time.monotonic()
        if key in self._cache:
            del self._cache[key]
        elif len(self._cache) >= self.max_size:
            self._cache.popitem(last=False)
        self._cache[key] = (t, value)

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {"size": len(self._cache), "max_size": self.max_size,
                "hits": self.hits, "misses": self.misses,
                "hit_rate": round(self.hits / max(total, 1) * 100, 1),
                "ttl_s": self.ttl_s}

    def clear(self) -> dict:
        evicted = len(self._cache)
        self._cache.clear()
        self.hits = self.misses = 0
        return {"evicted": evicted}
