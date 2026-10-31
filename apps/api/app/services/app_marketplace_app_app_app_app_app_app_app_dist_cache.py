"""Distributed cache manager — manage distributed cache clusters."""
from __future__ import annotations
from collections import defaultdict
import hashlib


class DistributedCache:
    def __init__(self, shards: int = 4):
        self._shards = shards
        self._data: dict[int, dict[str, str]] = {i: {} for i in range(shards)}
        self._hits = 0
        self._misses = 0

    def _shard(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16) % self._shards

    def set(self, key: str, value: str, ttl: int = 300) -> dict:
        shard = self._shard(key)
        self._data[shard][key] = value
        return {"key": key, "shard": shard, "cached": True}

    def get(self, key: str) -> dict:
        shard = self._shard(key)
        value = self._data[shard].get(key)
        if value is not None:
            self._hits += 1
            return {"key": key, "hit": True, "value": value, "shard": shard}
        self._misses += 1
        return {"key": key, "hit": False, "shard": shard}

    def delete(self, key: str) -> dict:
        shard = self._shard(key)
        removed = key in self._data[shard]
        self._data[shard].pop(key, None)
        return {"key": key, "deleted": removed}

    def flush_shard(self, shard: int) -> dict:
        count = len(self._data[shard])
        self._data[shard].clear()
        return {"shard": shard, "flushed": count}

    def stats(self) -> dict:
        total = self._hits + self._misses
        shard_sizes = {i: len(d) for i, d in self._data.items()}
        return {"shards": self._shards, "hits": self._hits, "misses": self._misses,
                "hit_rate": round(self._hits / max(total, 1) * 100, 1),
                "shard_sizes": shard_sizes,
                "total_keys": sum(shard_sizes.values())}
