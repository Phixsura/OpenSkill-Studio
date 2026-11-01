"""Vector Clock — track causality in distributed systems.

Implements:
- Per-node logical clocks
- Increment on local events
- Merge on message receive (element-wise max)
- Happens-before relationship detection
- Concurrent event detection (neither dominates)
- Clock comparison: before, after, concurrent, equal
"""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy


class VectorClock:
    def __init__(self, node_id: str = ""):
        self._clocks: dict[str, int] = {}
        self._node_id = node_id
        if node_id:
            self._clocks[node_id] = 0

    def increment(self, node_id: str = "") -> VectorClock:
        """Increment clock for a node (local event)."""
        nid = node_id or self._node_id
        self._clocks[nid] = self._clocks.get(nid, 0) + 1
        return self

    def merge(self, other: VectorClock) -> VectorClock:
        """Merge with another clock (receive message). Element-wise max."""
        all_nodes = set(self._clocks) | set(other._clocks)
        for node in all_nodes:
            self._clocks[node] = max(self._clocks.get(node, 0),
                                     other._clocks.get(node, 0))
        return self

    def get(self, node_id: str) -> int:
        return self._clocks.get(node_id, 0)

    def copy(self) -> VectorClock:
        vc = VectorClock(self._node_id)
        vc._clocks = dict(self._clocks)
        return vc

    def happens_before(self, other: VectorClock) -> bool:
        """True if self → other (self happened before other)."""
        if not self._clocks:
            return bool(other._clocks)
        at_least_one_less = False
        for node in set(self._clocks) | set(other._clocks):
            s = self._clocks.get(node, 0)
            o = other._clocks.get(node, 0)
            if s > o:
                return False
            if s < o:
                at_least_one_less = True
        return at_least_one_less

    def concurrent_with(self, other: VectorClock) -> bool:
        """True if neither happened before the other (conflict!)."""
        return (not self.happens_before(other) and
                not other.happens_before(self) and
                not self.equals(other))

    def equals(self, other: VectorClock) -> bool:
        all_nodes = set(self._clocks) | set(other._clocks)
        return all(self._clocks.get(n, 0) == other._clocks.get(n, 0)
                   for n in all_nodes)

    def compare(self, other: VectorClock) -> str:
        """Returns: 'before', 'after', 'concurrent', or 'equal'."""
        if self.equals(other):
            return "equal"
        if self.happens_before(other):
            return "before"
        if other.happens_before(self):
            return "after"
        return "concurrent"

    def to_dict(self) -> dict[str, int]:
        return dict(self._clocks)

    @classmethod
    def from_dict(cls, data: dict[str, int], node_id: str = "") -> VectorClock:
        vc = cls(node_id)
        vc._clocks = dict(data)
        return vc

    def __repr__(self) -> str:
        return f"VC({self._clocks})"


class VectorClockService:
    """Manage vector clocks for a distributed system."""

    def __init__(self):
        self._node_clocks: dict[str, VectorClock] = {}

    def register_node(self, node_id: str) -> VectorClock:
        vc = VectorClock(node_id)
        self._node_clocks[node_id] = vc
        return vc

    def local_event(self, node_id: str) -> VectorClock:
        vc = self._node_clocks.get(node_id)
        if not vc:
            raise ValueError(f"Node {node_id} not registered")
        vc.increment()
        return vc.copy()

    def send_message(self, sender: str) -> VectorClock:
        """Sender increments and returns clock to attach to message."""
        vc = self._node_clocks.get(sender)
        if not vc:
            raise ValueError(f"Node {sender} not registered")
        vc.increment()
        return vc.copy()

    def receive_message(self, receiver: str, sender_clock: VectorClock) -> VectorClock:
        """Receiver merges sender's clock and increments own."""
        vc = self._node_clocks.get(receiver)
        if not vc:
            raise ValueError(f"Node {receiver} not registered")
        vc.merge(sender_clock)
        vc.increment()
        return vc.copy()

    def compare_events(self, clock_a: VectorClock, clock_b: VectorClock) -> str:
        return clock_a.compare(clock_b)
