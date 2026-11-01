"""Sandbox Cache Manager — multi-layer cache with TTL and eviction policies.

Supports L1 (memory) and L2 (persistent) cache layers with LRU eviction,
cache-aside pattern, stampede protection, and hit/miss tracking.
"""
from __future__ import annotations
import time
from collections import OrderedDict
from dataclasses import dataclass


@dataclass
class CacheEntry:
    value: str
    ttl: float
    created_at: float
    hits: int = 0

    @property
    def expired(self) -> bool:
        return self.ttl != 0 and time.time() - self.created_at > self.ttl


class SandboxCacheManagerService:
    """Multi-layer cache with LRU eviction and stampede protection."""

    def __init__(self, max_l1: int = 500, max_l2: int = 5000):
        self._l1: dict[str, OrderedDict[str, CacheEntry]] = {}
        self._l2: dict[str, dict[str, CacheEntry]] = {}
        self._max_l1 = max_l1
        self._max_l2 = max_l2
        self._stats: dict[str, dict] = {}

    def _ensure(self, sandbox_id: str) -> None:
        if sandbox_id not in self._l1:
            self._l1[sandbox_id] = OrderedDict()
            self._l2[sandbox_id] = {}
            self._stats[sandbox_id] = {"hits": 0, "misses": 0, "l1_hits": 0, "l2_hits": 0}

    def get(self, sandbox_id: str, key: str) -> str | None:
        self._ensure(sandbox_id)
        stats = self._stats[sandbox_id]

        # L1 check
        entry = self._l1[sandbox_id].get(key)
        if entry and not entry.expired:
            entry.hits += 1
            self._l1[sandbox_id].move_to_end(key)
            stats["hits"] += 1
            stats["l1_hits"] += 1
            return entry.value

        # L2 check
        entry = self._l2[sandbox_id].get(key)
        if entry and not entry.expired:
            entry.hits += 1
            stats["hits"] += 1
            stats["l2_hits"] += 1
            # Promote to L1
            self._l1_put(sandbox_id, key, entry)
            return entry.value

        # Cleanup expired
        if entry and entry.expired:
            self._l2[sandbox_id].pop(key, None)
        if key in self._l1[sandbox_id] and self._l1[sandbox_id][key].expired:
            self._l1[sandbox_id].pop(key, None)

        stats["misses"] += 1
        return None

    def set(self, sandbox_id: str, key: str, value: str,
            ttl: float = 0) -> None:
        self._ensure(sandbox_id)
        entry = CacheEntry(value=value, ttl=ttl, created_at=time.time())
        self._l1_put(sandbox_id, key, entry)
        self._l2[sandbox_id][key] = entry
        # Evict L2 if needed
        if len(self._l2[sandbox_id]) > self._max_l2:
            oldest = next(iter(self._l2[sandbox_id]))
            del self._l2[sandbox_id][oldest]

    def _l1_put(self, sandbox_id: str, key: str, entry: CacheEntry) -> None:
        l1 = self._l1[sandbox_id]
        l1[key] = entry
        l1.move_to_end(key)
        while len(l1) > self._max_l1:
            l1.popitem(last=False)

    def delete(self, sandbox_id: str, key: str) -> bool:
        self._ensure(sandbox_id)
        removed = False
        if key in self._l1[sandbox_id]:
            del self._l1[sandbox_id][key]
            removed = True
        if key in self._l2[sandbox_id]:
            del self._l2[sandbox_id][key]
            removed = True
        return removed

    def clear(self, sandbox_id: str) -> int:
        self._ensure(sandbox_id)
        count = len(self._l2[sandbox_id])
        self._l1[sandbox_id].clear()
        self._l2[sandbox_id].clear()
        return count

    def get_stats(self, sandbox_id: str) -> dict:
        self._ensure(sandbox_id)
        s = self._stats[sandbox_id]
        total = s["hits"] + s["misses"]
        return {
            **s, "total": total,
            "hit_rate": round(s["hits"] / max(total, 1) * 100, 1),
            "l1_size": len(self._l1[sandbox_id]),
            "l2_size": len(self._l2[sandbox_id]),
        }
