"""CRDT Counter — conflict-free replicated counters for distributed systems.

CRDTs: data structures that can be replicated across nodes and
merged without conflicts. Eventual consistency guaranteed.

Implements:
- G-Counter (grow-only): each node tracks its own increments
- PN-Counter (positive-negative): pair of G-Counters for inc/dec
- Merge operation: element-wise max (commutative, associative, idempotent)
- Multi-node simulation
"""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy


class GCounter:
    """Grow-only counter: supports increment, not decrement."""

    def __init__(self, node_id: str):
        self._node_id = node_id
        self._counts: dict[str, int] = {node_id: 0}

    def increment(self, amount: int = 1) -> None:
        if amount < 0:
            raise ValueError("G-Counter only supports increment")
        self._counts[self._node_id] = self._counts.get(self._node_id, 0) + amount

    @property
    def value(self) -> int:
        return sum(self._counts.values())

    def merge(self, other: GCounter) -> GCounter:
        """Merge: element-wise max. Commutative + associative + idempotent."""
        result = GCounter(self._node_id)
        all_nodes = set(self._counts) | set(other._counts)
        result._counts = {n: max(self._counts.get(n, 0), other._counts.get(n, 0))
                          for n in all_nodes}
        return result

    def to_dict(self) -> dict:
        return {"type": "g-counter", "node": self._node_id,
                "counts": dict(self._counts)}

    @classmethod
    def from_dict(cls, data: dict) -> GCounter:
        gc = cls(data["node"])
        gc._counts = dict(data["counts"])
        return gc


class PNCounter:
    """Positive-Negative counter: supports both increment and decrement."""

    def __init__(self, node_id: str):
        self._node_id = node_id
        self._positive = GCounter(node_id)
        self._negative = GCounter(node_id)

    def increment(self, amount: int = 1) -> None:
        self._positive.increment(amount)

    def decrement(self, amount: int = 1) -> None:
        self._negative.increment(amount)

    @property
    def value(self) -> int:
        return self._positive.value - self._negative.value

    def merge(self, other: PNCounter) -> PNCounter:
        result = PNCounter(self._node_id)
        result._positive = self._positive.merge(other._positive)
        result._negative = self._negative.merge(other._negative)
        return result


class CrdtCounterService:
    """Manage CRDT counters across simulated distributed nodes."""

    def __init__(self):
        self._g_counters: dict[str, dict[str, GCounter]] = {}  # name -> {node -> counter}
        self._pn_counters: dict[str, dict[str, PNCounter]] = {}

    def create_g_counter(self, name: str, nodes: list[str]) -> None:
        self._g_counters[name] = {n: GCounter(n) for n in nodes}

    def create_pn_counter(self, name: str, nodes: list[str]) -> None:
        self._pn_counters[name] = {n: PNCounter(n) for n in nodes}

    def g_increment(self, name: str, node_id: str, amount: int = 1) -> int:
        counter = self._g_counters.get(name, {}).get(node_id)
        if not counter:
            raise ValueError(f"Counter {name} on {node_id} not found")
        counter.increment(amount)
        return counter.value

    def pn_increment(self, name: str, node_id: str, amount: int = 1) -> int:
        counter = self._pn_counters.get(name, {}).get(node_id)
        if not counter:
            raise ValueError(f"Counter {name} on {node_id} not found")
        counter.increment(amount)
        return counter.value

    def pn_decrement(self, name: str, node_id: str, amount: int = 1) -> int:
        counter = self._pn_counters.get(name, {}).get(node_id)
        if not counter:
            raise ValueError(f"Counter {name} on {node_id} not found")
        counter.decrement(amount)
        return counter.value

    def sync_g(self, name: str) -> int:
        """Sync all nodes: merge all replicas. Returns converged value."""
        counters = self._g_counters.get(name, {})
        if not counters:
            return 0
        merged = None
        for counter in counters.values():
            if merged is None:
                merged = counter
            else:
                merged = merged.merge(counter)
        # Update all nodes to merged state
        if merged:
            for node_id in counters:
                counters[node_id] = GCounter.from_dict({
                    "node": node_id, "counts": dict(merged._counts)})
        return merged.value if merged else 0

    def sync_pn(self, name: str) -> int:
        counters = self._pn_counters.get(name, {})
        if not counters:
            return 0
        nodes = list(counters.keys())
        merged = counters[nodes[0]]
        for n in nodes[1:]:
            merged = merged.merge(counters[n])
        return merged.value

    def get_g_value(self, name: str, node_id: str) -> int:
        return self._g_counters.get(name, {}).get(node_id, GCounter("")).value

    def get_pn_value(self, name: str, node_id: str) -> int:
        return self._pn_counters.get(name, {}).get(node_id, PNCounter("")).value
