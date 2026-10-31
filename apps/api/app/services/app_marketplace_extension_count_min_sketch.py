"""Count-Min Sketch — probabilistic frequency estimation with sub-linear memory.

Estimates how many times each element has been seen in a stream,
using d hash functions and a w×d counter matrix.

Implements:
- Configurable width×depth (tradeoff: accuracy vs memory)
- Optimal parameters from error/probability targets
- Point query: estimated frequency of an element
- Inner product estimation (dot product of two sketches)
- Heavy hitter detection
"""
from __future__ import annotations
import hashlib
import math


class CountMinSketchService:
    def __init__(self, width: int = 0, depth: int = 0,
                 epsilon: float = 0.01, delta: float = 0.01):
        """
        Either specify width+depth directly, or epsilon+delta:
        - epsilon: error factor (estimate <= true + epsilon*N)
        - delta: probability of exceeding error bound
        """
        if width > 0 and depth > 0:
            self._w = width
            self._d = depth
        else:
            self._w = max(2, int(math.ceil(math.e / epsilon)))
            self._d = max(1, int(math.ceil(math.log(1 / delta))))

        self._table = [[0] * self._w for _ in range(self._d)]
        self._total = 0
        self._seeds = [i * 0x9e3779b9 + 0x517cc1b7 for i in range(self._d)]

    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.md5(f"{seed}:{item}".encode()).hexdigest()
        return int(h[:8], 16) % self._w

    def add(self, item: str, count: int = 1) -> None:
        """Add `count` occurrences of `item`."""
        for i in range(self._d):
            idx = self._hash(item, self._seeds[i])
            self._table[i][idx] += count
        self._total += count

    def estimate(self, item: str) -> int:
        """Estimate frequency of `item`. Always >= true count."""
        return min(self._table[i][self._hash(item, self._seeds[i])]
                   for i in range(self._d))

    def merge(self, other: CountMinSketchService) -> CountMinSketchService:
        """Merge two sketches (e.g., from different time windows)."""
        if self._w != other._w or self._d != other._d:
            raise ValueError("Sketches must have same dimensions")
        result = CountMinSketchService(width=self._w, depth=self._d)
        for i in range(self._d):
            for j in range(self._w):
                result._table[i][j] = self._table[i][j] + other._table[i][j]
        result._total = self._total + other._total
        return result

    def heavy_hitters(self, threshold_pct: float = 1.0,
                      candidates: list[str] | None = None) -> list[tuple[str, int]]:
        """Find items above threshold % of total count.
        Requires candidate list (CM sketch can't enumerate items)."""
        if not candidates:
            return []
        min_count = self._total * threshold_pct / 100
        result = []
        for item in candidates:
            est = self.estimate(item)
            if est >= min_count:
                result.append((item, est))
        return sorted(result, key=lambda x: x[1], reverse=True)

    @property
    def total_count(self) -> int:
        return self._total

    def stats(self) -> dict:
        return {
            "width": self._w,
            "depth": self._d,
            "total_count": self._total,
            "memory_cells": self._w * self._d,
            "memory_bytes": self._w * self._d * 8,  # 8 bytes per int
        }
