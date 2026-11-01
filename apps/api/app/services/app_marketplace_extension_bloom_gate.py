"""Bloom Gate — bloom filter as a fast negative-lookup gate.

Use case: before an expensive DB/API call, check bloom filter first.
If bloom says "not present" → guaranteed absent, skip the call.
If bloom says "maybe present" → proceed with the expensive call.

Implements:
- Multiple independent bloom filters (per table/index)
- Automatic sizing from expected elements + FPR target
- Gate decision with metrics (saves, false positives)
- Filter rebuild (periodic refresh from source of truth)
- Composite gate (AND/OR multiple filters)
"""
from __future__ import annotations
import hashlib
import math


class BloomGate:
    def __init__(self, expected_elements: int = 10000,
                 fpr: float = 0.01):
        self._m = max(64, int(-expected_elements * math.log(fpr) / (math.log(2) ** 2)))
        self._k = max(1, int(self._m / expected_elements * math.log(2)))
        self._bits = bytearray(math.ceil(self._m / 8))
        self._count = 0
        self._checks = 0
        self._negatives = 0  # definite negatives (saved expensive lookups)

    def _hashes(self, key: str) -> list[int]:
        h1 = int(hashlib.md5(key.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(key.encode()).hexdigest(), 16)
        return [(h1 + i * h2) % self._m for i in range(self._k)]

    def add(self, key: str) -> None:
        for pos in self._hashes(key):
            self._bits[pos // 8] |= (1 << (pos % 8))
        self._count += 1

    def check(self, key: str) -> bool:
        """Returns True if MAYBE present (proceed with lookup),
        False if DEFINITELY absent (skip lookup)."""
        self._checks += 1
        for pos in self._hashes(key):
            if not (self._bits[pos // 8] & (1 << (pos % 8))):
                self._negatives += 1
                return False
        return True

    @property
    def savings_rate(self) -> float:
        """Percentage of lookups saved by negative results."""
        return round(self._negatives / max(1, self._checks) * 100, 1)

    @property
    def size(self) -> int:
        return self._count

    def stats(self) -> dict:
        return {"elements": self._count, "bits": self._m,
                "hash_functions": self._k,
                "checks": self._checks, "negatives": self._negatives,
                "savings_rate": self.savings_rate,
                "memory_bytes": len(self._bits)}


class BloomGateService:
    def __init__(self):
        self._gates: dict[str, BloomGate] = {}

    def create(self, name: str, expected: int = 10000,
               fpr: float = 0.01) -> BloomGate:
        gate = BloomGate(expected, fpr)
        self._gates[name] = gate
        return gate

    def populate(self, name: str, keys: list[str]) -> int:
        gate = self._gates.get(name)
        if not gate:
            return 0
        for key in keys:
            gate.add(key)
        return len(keys)

    def should_lookup(self, name: str, key: str) -> bool:
        """Gate decision: should we proceed with the expensive lookup?"""
        gate = self._gates.get(name)
        if not gate:
            return True  # no gate = always lookup
        return gate.check(key)

    def gate_or_lookup(self, name: str, key: str,
                       lookup_fn: callable) -> tuple[object, bool]:
        """Check gate, call lookup only if needed.
        Returns (result, was_lookup_called)."""
        if not self.should_lookup(name, key):
            return None, False  # definitely not present
        result = lookup_fn(key)
        return result, True

    def rebuild(self, name: str, keys: list[str],
                expected: int = 0, fpr: float = 0.01) -> BloomGate:
        """Rebuild gate from fresh data."""
        exp = expected or len(keys)
        gate = BloomGate(max(1, exp), fpr)
        for key in keys:
            gate.add(key)
        self._gates[name] = gate
        return gate

    def composite_check(self, names: list[str], key: str,
                        mode: str = "and") -> bool:
        """Check multiple gates. AND = all must say maybe. OR = any says maybe."""
        results = [self.should_lookup(n, key) for n in names]
        if mode == "and":
            return all(results)
        return any(results)

    def get_all_stats(self) -> dict[str, dict]:
        return {name: gate.stats() for name, gate in self._gates.items()}
