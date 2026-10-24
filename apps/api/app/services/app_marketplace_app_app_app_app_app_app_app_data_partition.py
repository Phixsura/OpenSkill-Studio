"""Data partitioner — partition data across shards for horizontal scaling."""
from __future__ import annotations
import hashlib


class DataPartitioner:
    def __init__(self, num_shards: int = 4):
        self._num_shards = num_shards
        self._shard_counts: dict[int, int] = {i: 0 for i in range(num_shards)}

    def partition(self, key: str) -> dict:
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        shard = h % self._num_shards
        self._shard_counts[shard] += 1
        return {"key": key, "shard": shard, "shard_name": f"shard-{shard}"}

    def batch_partition(self, keys: list[str]) -> dict:
        by_shard: dict[int, list[str]] = {i: [] for i in range(self._num_shards)}
        for key in keys:
            r = self.partition(key)
            by_shard[r["shard"]].append(key)
        return {"total": len(keys), "by_shard": {f"shard-{k}": len(v) for k, v in by_shard.items()}}

    def rebalance_needed(self, threshold_pct: float = 30) -> dict:
        total = sum(self._shard_counts.values())
        if total == 0:
            return {"needed": False, "reason": "no_data"}
        expected = total / self._num_shards
        max_deviation = max(abs(c - expected) / max(expected, 1) * 100 for c in self._shard_counts.values())
        return {"needed": max_deviation > threshold_pct,
                "max_deviation_pct": round(max_deviation, 1),
                "distribution": dict(self._shard_counts)}
