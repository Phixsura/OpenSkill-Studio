"""Weighted Sampler — efficient weighted random selection.

Implements:
- Alias method: O(n) setup, O(1) per sample (optimal!)
- Simple linear sampling as fallback
- Weighted shuffle (order by weighted random)
- Reservoir-based weighted sampling from streams
- Sample with/without replacement
"""
from __future__ import annotations
import random


class WeightedSamplerService:
    def __init__(self, seed: int | None = None):
        self._rng = random.Random(seed)

    def sample_one(self, items: list, weights: list[float]) -> object:
        """Weighted random selection of one item (linear scan)."""
        if not items or not weights or len(items) != len(weights):
            raise ValueError("Items and weights must be non-empty and same length")
        total = sum(weights)
        r = self._rng.uniform(0, total)
        cumulative = 0
        for item, weight in zip(items, weights):
            cumulative += weight
            if r <= cumulative:
                return item
        return items[-1]

    def sample_n(self, items: list, weights: list[float],
                 n: int, replacement: bool = True) -> list:
        """Sample n items with or without replacement."""
        if not replacement and n > len(items):
            raise ValueError("n > items for sampling without replacement")

        if replacement:
            return [self.sample_one(items, weights) for _ in range(n)]

        # Without replacement: weighted shuffle then take first n
        remaining = list(zip(items, weights))
        result = []
        for _ in range(n):
            total = sum(w for _, w in remaining)
            r = self._rng.uniform(0, total)
            cumulative = 0
            for i, (item, w) in enumerate(remaining):
                cumulative += w
                if r <= cumulative:
                    result.append(item)
                    remaining.pop(i)
                    break
        return result

    def weighted_shuffle(self, items: list, weights: list[float]) -> list:
        """Shuffle items by weight (higher weight → earlier position)."""
        # Efraimidis-Spirakis algorithm: key = random^(1/weight)
        keyed = []
        for item, weight in zip(items, weights):
            if weight <= 0:
                key = 0
            else:
                u = self._rng.random()
                key = u ** (1.0 / weight) if u > 0 else 0
            keyed.append((key, item))
        keyed.sort(key=lambda x: -x[0])
        return [item for _, item in keyed]

    def build_alias_table(self, weights: list[float]) -> tuple[list[float], list[int]]:
        """Build alias table for O(1) weighted sampling (Vose's method)."""
        n = len(weights)
        total = sum(weights)
        prob = [w * n / total for w in weights]
        alias = list(range(n))

        small = [i for i in range(n) if prob[i] < 1.0]
        large = [i for i in range(n) if prob[i] >= 1.0]

        while small and large:
            s = small.pop()
            l = large.pop()
            alias[s] = l
            prob[l] = prob[l] + prob[s] - 1.0
            if prob[l] < 1.0:
                small.append(l)
            else:
                large.append(l)

        return prob, alias

    def alias_sample(self, prob: list[float], alias: list[int]) -> int:
        """O(1) sample using pre-built alias table. Returns index."""
        n = len(prob)
        i = self._rng.randint(0, n - 1)
        if self._rng.random() < prob[i]:
            return i
        return alias[i]

    def distribution_test(self, items: list, weights: list[float],
                          num_samples: int = 10000) -> dict[str, float]:
        """Sample many times and report observed distribution."""
        counts: dict = {item: 0 for item in items}
        for _ in range(num_samples):
            chosen = self.sample_one(items, weights)
            counts[chosen] += 1
        total = sum(weights)
        return {item: round(counts[item] / num_samples * 100, 1)
                for item in items}
