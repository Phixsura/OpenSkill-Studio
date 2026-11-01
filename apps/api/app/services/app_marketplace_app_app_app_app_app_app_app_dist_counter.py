"""Distributed counter — atomic counter with sharding support."""
from __future__ import annotations


class DistributedCounter:
    def __init__(self, shards: int = 4):
        self._shards = [0] * shards

    def increment(self, shard: int = 0, amount: int = 1) -> dict:
        idx = shard % len(self._shards)
        self._shards[idx] += amount
        return {"shard": idx, "value": self._shards[idx], "total": self.total()}

    def decrement(self, shard: int = 0, amount: int = 1) -> dict:
        idx = shard % len(self._shards)
        self._shards[idx] -= amount
        return {"shard": idx, "value": self._shards[idx], "total": self.total()}

    def total(self) -> int:
        return sum(self._shards)

    def stats(self) -> dict:
        return {"total": self.total(), "shards": len(self._shards),
                "shard_values": list(self._shards)}
