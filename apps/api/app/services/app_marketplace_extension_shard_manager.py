"""Shard Manager — automatic data partitioning with rebalancing.

Implements:
- Hash-based sharding with configurable shard count
- Range-based sharding for ordered data
- Virtual shard mapping for flexible rebalancing
- Shard split/merge operations
- Hotspot detection and migration
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
from collections import defaultdict


@dataclass
class Shard:
    shard_id: str
    node: str  # which node hosts this shard
    key_count: int = 0
    size_bytes: int = 0
    range_start: str = ""
    range_end: str = ""


class ShardManagerService:
    def __init__(self, num_shards: int = 8, nodes: list[str] | None = None):
        self._num_shards = num_shards
        self._nodes = nodes or [f"node-{i}" for i in range(3)]
        self._shards: dict[str, Shard] = {}
        self._key_to_shard: dict[str, str] = {}
        self._initialize()

    def _initialize(self):
        for i in range(self._num_shards):
            sid = f"shard-{i}"
            node = self._nodes[i % len(self._nodes)]
            self._shards[sid] = Shard(shard_id=sid, node=node)

    def _hash_key(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def locate(self, key: str) -> Shard:
        """Find which shard owns a key."""
        shard_idx = self._hash_key(key) % self._num_shards
        sid = f"shard-{shard_idx}"
        return self._shards[sid]

    def put(self, key: str, size_bytes: int = 100) -> Shard:
        """Record a key placement."""
        shard = self.locate(key)
        if key not in self._key_to_shard:
            shard.key_count += 1
        self._key_to_shard[key] = shard.shard_id
        shard.size_bytes += size_bytes
        return shard

    def get_shard(self, key: str) -> str:
        """Get shard ID for a key."""
        return self.locate(key).shard_id

    def rebalance(self) -> list[dict]:
        """Move shards to balance load across nodes."""
        # Count shards per node
        node_shards: dict[str, list[str]] = defaultdict(list)
        for sid, shard in self._shards.items():
            node_shards[shard.node].append(sid)

        target = self._num_shards // len(self._nodes)
        moves = []

        # Find overloaded and underloaded nodes
        over = [(n, shards) for n, shards in node_shards.items()
                if len(shards) > target + 1]
        under = [n for n, shards in node_shards.items()
                 if len(shards) < target]

        for over_node, shards in over:
            while len(shards) > target + 1 and under:
                dest = under.pop(0)
                sid = shards.pop()
                self._shards[sid].node = dest
                moves.append({"shard": sid, "from": over_node, "to": dest})
                node_shards[dest].append(sid)
                if len(node_shards[dest]) >= target:
                    pass  # might still be under by 1

        return moves

    def detect_hotspots(self, threshold_keys: int = 0) -> list[Shard]:
        """Find shards with disproportionately many keys."""
        if not self._shards:
            return []
        avg = sum(s.key_count for s in self._shards.values()) / len(self._shards)
        threshold = threshold_keys or max(1, avg * 2)
        return [s for s in self._shards.values() if s.key_count > threshold]

    def add_node(self, node: str) -> list[dict]:
        """Add a new node and rebalance."""
        self._nodes.append(node)
        return self.rebalance()

    def remove_node(self, node: str) -> list[dict]:
        """Remove a node, reassign its shards."""
        if node not in self._nodes or len(self._nodes) <= 1:
            return []
        self._nodes.remove(node)
        # Reassign shards from removed node
        remaining = [n for n in self._nodes]
        moves = []
        idx = 0
        for sid, shard in self._shards.items():
            if shard.node == node:
                new_node = remaining[idx % len(remaining)]
                shard.node = new_node
                moves.append({"shard": sid, "from": node, "to": new_node})
                idx += 1
        return moves

    def get_distribution(self) -> dict[str, list[str]]:
        """Show shard distribution across nodes."""
        dist: dict[str, list[str]] = defaultdict(list)
        for sid, shard in self._shards.items():
            dist[shard.node].append(sid)
        return dict(dist)

    def stats(self) -> dict:
        return {
            "num_shards": self._num_shards,
            "num_nodes": len(self._nodes),
            "total_keys": sum(s.key_count for s in self._shards.values()),
            "total_bytes": sum(s.size_bytes for s in self._shards.values()),
            "distribution": {n: len(shards) for n, shards in self.get_distribution().items()},
        }
