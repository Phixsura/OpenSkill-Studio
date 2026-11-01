"""Consistent Hash Ring — distribute keys across nodes with minimal rehashing.

Implements:
- Consistent hashing with configurable virtual nodes per physical node
- O(log n) key lookup via binary search on sorted ring
- Minimal rehashing when nodes join/leave (~K/N keys move)
- Key distribution statistics
"""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import bisect


@dataclass
class HashNode:
    node_id: str
    host: str
    weight: int = 1  # more weight = more virtual nodes


class ConsistentHashRingService:
    def __init__(self, virtual_nodes: int = 150):
        self._virtual_nodes = virtual_nodes
        self._ring: list[tuple[int, str]] = []  # sorted (hash, node_id)
        self._ring_hashes: list[int] = []  # just hashes for bisect
        self._nodes: dict[str, HashNode] = {}

    def _hash(self, key: str) -> int:
        return int(hashlib.md5(key.encode()).hexdigest(), 16)

    def add_node(self, node_id: str, host: str, weight: int = 1) -> int:
        """Returns number of virtual nodes added."""
        if node_id in self._nodes:
            raise ValueError(f"Node {node_id} already exists")
        node = HashNode(node_id=node_id, host=host, weight=weight)
        self._nodes[node_id] = node

        vnodes = self._virtual_nodes * weight
        for i in range(vnodes):
            h = self._hash(f"{node_id}:vnode:{i}")
            bisect.insort(self._ring_hashes, h)
            # Insert maintaining sort
            idx = bisect.bisect_left(self._ring_hashes, h)
            self._ring.insert(idx, (h, node_id))
        return vnodes

    def remove_node(self, node_id: str) -> int:
        """Returns number of virtual nodes removed."""
        if node_id not in self._nodes:
            return 0
        node = self._nodes.pop(node_id)
        vnodes = self._virtual_nodes * node.weight
        # Remove all virtual nodes for this node
        new_ring = [(h, nid) for h, nid in self._ring if nid != node_id]
        self._ring = new_ring
        self._ring_hashes = [h for h, _ in new_ring]
        return vnodes

    def get_node(self, key: str) -> str | None:
        """O(log n) lookup: find the first node clockwise from key's hash."""
        if not self._ring:
            return None
        h = self._hash(key)
        idx = bisect.bisect_right(self._ring_hashes, h)
        if idx >= len(self._ring):
            idx = 0  # wrap around
        return self._ring[idx][1]

    def get_nodes(self, key: str, count: int = 3) -> list[str]:
        """Get multiple nodes for replication (unique physical nodes)."""
        if not self._ring:
            return []
        h = self._hash(key)
        idx = bisect.bisect_right(self._ring_hashes, h)
        seen = set()
        result = []
        for i in range(len(self._ring)):
            pos = (idx + i) % len(self._ring)
            node_id = self._ring[pos][1]
            if node_id not in seen:
                seen.add(node_id)
                result.append(node_id)
                if len(result) >= count:
                    break
        return result

    def get_distribution(self, sample_keys: list[str]) -> dict[str, int]:
        """Check how keys distribute across nodes."""
        dist: dict[str, int] = {nid: 0 for nid in self._nodes}
        for key in sample_keys:
            node = self.get_node(key)
            if node:
                dist[node] = dist.get(node, 0) + 1
        return dist

    def stats(self) -> dict:
        return {
            "physical_nodes": len(self._nodes),
            "virtual_nodes": len(self._ring),
            "ring_size": len(self._ring),
        }
