"""HyperLogLog — probabilistic cardinality estimation with O(1) memory.

Estimates the number of distinct elements in a stream using
O(m) memory where m = 2^p registers, regardless of input size.

Implements:
- Register-based counting with harmonic mean
- Configurable precision (p = 4..16, registers = 2^p)
- Small range correction (linear counting)
- Large range correction
- Merge operation for distributed counting
"""
from __future__ import annotations
import hashlib
import math


class HyperLogLogService:
    def __init__(self, precision: int = 14):
        """precision p: uses 2^p registers. Higher = more accurate, more memory."""
        if not 4 <= precision <= 16:
            raise ValueError("Precision must be 4-16")
        self._p = precision
        self._m = 1 << precision  # number of registers
        self._registers = [0] * self._m
        self._alpha = self._compute_alpha(self._m)

    @staticmethod
    def _compute_alpha(m: int) -> float:
        if m == 16:
            return 0.673
        if m == 32:
            return 0.697
        if m == 64:
            return 0.709
        return 0.7213 / (1 + 1.079 / m)

    def _hash(self, item: str) -> int:
        return int(hashlib.sha1(item.encode()).hexdigest(), 16)

    def _rho(self, bits: int) -> int:
        """Position of leftmost 1-bit (1-indexed). rho(0) = max."""
        if bits == 0:
            return 64 - self._p
        pos = 1
        while (bits & 1) == 0:
            bits >>= 1
            pos += 1
        return pos

    def add(self, item: str) -> None:
        h = self._hash(item)
        # First p bits determine register
        idx = h & (self._m - 1)
        # Remaining bits for counting leading zeros
        remaining = h >> self._p
        self._registers[idx] = max(self._registers[idx], self._rho(remaining))

    def count(self) -> int:
        """Estimate cardinality."""
        # Raw harmonic mean estimate
        indicator = sum(2.0 ** (-r) for r in self._registers)
        estimate = self._alpha * self._m * self._m / indicator

        # Small range correction
        if estimate <= 2.5 * self._m:
            zeros = self._registers.count(0)
            if zeros > 0:
                estimate = self._m * math.log(self._m / zeros)  # linear counting

        # Large range correction (not needed for 64-bit hashes in practice)
        # Included for completeness
        two_32 = 2 ** 32
        if estimate > two_32 / 30:
            estimate = -two_32 * math.log(1 - estimate / two_32)

        return int(round(estimate))

    def merge(self, other: HyperLogLogService) -> HyperLogLogService:
        """Merge two HLLs (e.g., from different servers). Returns new HLL."""
        if self._p != other._p:
            raise ValueError("Cannot merge HLLs with different precision")
        result = HyperLogLogService(self._p)
        result._registers = [max(a, b)
                              for a, b in zip(self._registers, other._registers)]
        return result

    def relative_error(self) -> float:
        """Expected relative error: 1.04 / sqrt(m)."""
        return round(1.04 / math.sqrt(self._m), 4)

    def memory_bytes(self) -> int:
        """Memory usage: 1 byte per register (values 0-63 fit in 6 bits)."""
        return self._m
