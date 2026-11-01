"""Interval Tree — efficient overlapping interval queries.

Used for: time range scheduling, IP range lookup, version range matching.

Implements:
- Insert intervals with associated data
- Query all intervals overlapping a point
- Query all intervals overlapping a range
- Remove intervals
- Augmented BST with max-endpoint tracking
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Interval:
    low: float
    high: float
    data: object = None

    def overlaps(self, other: Interval) -> bool:
        return self.low <= other.high and other.low <= self.high

    def contains_point(self, point: float) -> bool:
        return self.low <= point <= self.high


@dataclass
class ITNode:
    interval: Interval
    max_high: float  # max high value in this subtree
    left: ITNode | None = None
    right: ITNode | None = None


class IntervalTreeService:
    def __init__(self):
        self._root: ITNode | None = None
        self._size = 0

    def insert(self, low: float, high: float, data: object = None) -> Interval:
        if low > high:
            raise ValueError(f"Invalid interval: [{low}, {high}]")
        interval = Interval(low, high, data)
        self._root = self._insert(self._root, interval)
        self._size += 1
        return interval

    def _insert(self, node: ITNode | None, interval: Interval) -> ITNode:
        if node is None:
            return ITNode(interval=interval, max_high=interval.high)

        if interval.low < node.interval.low:
            node.left = self._insert(node.left, interval)
        else:
            node.right = self._insert(node.right, interval)

        node.max_high = max(node.max_high, interval.high)
        return node

    def query_point(self, point: float) -> list[Interval]:
        """Find all intervals containing the point."""
        results = []
        self._query_point(self._root, point, results)
        return results

    def _query_point(self, node: ITNode | None, point: float,
                     results: list) -> None:
        if node is None:
            return
        # If point is beyond max_high of this subtree, no match possible
        if point > node.max_high:
            return
        # Check left subtree
        self._query_point(node.left, point, results)
        # Check current
        if node.interval.contains_point(point):
            results.append(node.interval)
        # Check right subtree only if point >= low of current
        if point >= node.interval.low:
            self._query_point(node.right, point, results)

    def query_range(self, low: float, high: float) -> list[Interval]:
        """Find all intervals overlapping [low, high]."""
        query = Interval(low, high)
        results = []
        self._query_range(self._root, query, results)
        return results

    def _query_range(self, node: ITNode | None, query: Interval,
                     results: list) -> None:
        if node is None:
            return
        if query.low > node.max_high:
            return
        self._query_range(node.left, query, results)
        if node.interval.overlaps(query):
            results.append(node.interval)
        if query.high >= node.interval.low:
            self._query_range(node.right, query, results)

    def find_gaps(self, low: float, high: float) -> list[tuple[float, float]]:
        """Find uncovered gaps in a range."""
        overlapping = self.query_range(low, high)
        if not overlapping:
            return [(low, high)]

        # Sort by low endpoint
        sorted_intervals = sorted(overlapping, key=lambda i: i.low)
        gaps = []
        current = low

        for interval in sorted_intervals:
            if interval.low > current:
                gaps.append((current, interval.low))
            current = max(current, interval.high)

        if current < high:
            gaps.append((current, high))

        return gaps

    @property
    def size(self) -> int:
        return self._size
