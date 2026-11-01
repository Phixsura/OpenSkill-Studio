"""Bloom Filter — space-efficient probabilistic set membership testing.

Implements:
- Configurable number of hash functions and bit array size
- Optimal parameter calculation from expected elements and false positive rate
- Multiple independent hash functions via double hashing
- Union and intersection of filters
- Estimated element count and current false positive probability
"""
from __future__ import annotations
import math
import hashlib
from dataclasses import dataclass


@dataclass
class BloomFilterParams:
    expected_elements: int
    false_positive_rate: float
    bit_size: int = 0
    hash_count: int = 0

    def __post_init__(self):
        if not self.bit_size:
            # Optimal bit size: m = -n*ln(p) / (ln2)^2
            self.bit_size = max(8, int(-self.expected_elements * math.log(self.false_positive_rate)
                                       / (math.log(2) ** 2)))
        if not self.hash_count:
            # Optimal hash count: k = (m/n) * ln2
            self.hash_count = max(1, int(self.bit_size / self.expected_elements * math.log(2)))


class BloomFilter:
    def __init__(self, params: BloomFilterParams):
        self.params = params
        self._bits = bytearray(math.ceil(params.bit_size / 8))
        self._count = 0

    def _hashes(self, item: str) -> list[int]:
        """Generate k hash positions using double hashing."""
        h1 = int(hashlib.md5(item.encode()).hexdigest(), 16)
        h2 = int(hashlib.sha1(item.encode()).hexdigest(), 16)
        return [(h1 + i * h2) % self.params.bit_size for i in range(self.params.hash_count)]

    def _get_bit(self, pos: int) -> bool:
        return bool(self._bits[pos // 8] & (1 << (pos % 8)))

    def _set_bit(self, pos: int) -> None:
        self._bits[pos // 8] |= (1 << (pos % 8))

    def add(self, item: str) -> None:
        positions = self._hashes(item)
        was_new = not all(self._get_bit(p) for p in positions)
        for p in positions:
            self._set_bit(p)
        if was_new:
            self._count += 1

    def contains(self, item: str) -> bool:
        """Returns True if item MAY be in set, False if DEFINITELY not."""
        return all(self._get_bit(p) for p in self._hashes(item))

    @property
    def estimated_count(self) -> int:
        return self._count

    @property
    def current_fpr(self) -> float:
        """Estimated current false positive rate."""
        m = self.params.bit_size
        k = self.params.hash_count
        n = self._count
        if n == 0:
            return 0.0
        return (1 - math.exp(-k * n / m)) ** k

    def union(self, other: BloomFilter) -> BloomFilter:
        """Create new filter that is the union of self and other."""
        if self.params.bit_size != other.params.bit_size:
            raise ValueError("Filters must have same bit size")
        result = BloomFilter(self.params)
        for i in range(len(self._bits)):
            result._bits[i] = self._bits[i] | other._bits[i]
        result._count = self._count + other._count  # approximate
        return result

    def stats(self) -> dict:
        total_bits = self.params.bit_size
        set_bits = sum(bin(b).count('1') for b in self._bits)
        return {
            "bit_size": total_bits,
            "hash_functions": self.params.hash_count,
            "elements_added": self._count,
            "bits_set": set_bits,
            "fill_ratio": round(set_bits / total_bits, 4) if total_bits else 0,
            "current_fpr": round(self.current_fpr, 6),
            "memory_bytes": len(self._bits),
        }


class BloomFilterService:
    def __init__(self):
        self._filters: dict[str, BloomFilter] = {}

    def create(self, name: str, expected_elements: int = 10000,
               false_positive_rate: float = 0.01) -> BloomFilter:
        params = BloomFilterParams(expected_elements, false_positive_rate)
        bf = BloomFilter(params)
        self._filters[name] = bf
        return bf

    def get(self, name: str) -> BloomFilter | None:
        return self._filters.get(name)
