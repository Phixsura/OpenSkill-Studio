"""Sparse Bitset — memory-efficient set operations on large integer domains.

Unlike dense bitsets that allocate full range, sparse bitsets only store
occupied chunks. Ideal for user ID sets, feature flags across millions of IDs.

Implements:
- Set/clear/test individual bits
- Bulk operations: AND, OR, XOR, NOT (between two bitsets)
- Population count (cardinality)
- Iteration over set bits
- Serialization (for storage)
"""
from __future__ import annotations
from dataclasses import dataclass, field

CHUNK_SIZE = 64  # bits per chunk (one int)


class SparseBitset:
    def __init__(self):
        self._chunks: dict[int, int] = {}  # chunk_index -> 64-bit integer
        self._count = 0

    def _chunk_and_offset(self, bit: int) -> tuple[int, int]:
        return bit // CHUNK_SIZE, bit % CHUNK_SIZE

    def set(self, bit: int) -> None:
        """Set bit to 1."""
        chunk, offset = self._chunk_and_offset(bit)
        old = self._chunks.get(chunk, 0)
        new = old | (1 << offset)
        if new != old:
            self._count += 1
        self._chunks[chunk] = new

    def clear(self, bit: int) -> None:
        """Set bit to 0."""
        chunk, offset = self._chunk_and_offset(bit)
        old = self._chunks.get(chunk, 0)
        new = old & ~(1 << offset)
        if new != old:
            self._count -= 1
        if new == 0:
            self._chunks.pop(chunk, None)
        else:
            self._chunks[chunk] = new

    def test(self, bit: int) -> bool:
        """Test if bit is set."""
        chunk, offset = self._chunk_and_offset(bit)
        return bool(self._chunks.get(chunk, 0) & (1 << offset))

    def toggle(self, bit: int) -> bool:
        """Toggle bit. Returns new value."""
        if self.test(bit):
            self.clear(bit)
            return False
        self.set(bit)
        return True

    @property
    def cardinality(self) -> int:
        """Number of set bits."""
        return self._count

    def iter_set_bits(self) -> list[int]:
        """Return all set bit positions in order."""
        result = []
        for chunk_idx in sorted(self._chunks):
            value = self._chunks[chunk_idx]
            base = chunk_idx * CHUNK_SIZE
            for offset in range(CHUNK_SIZE):
                if value & (1 << offset):
                    result.append(base + offset)
        return result

    def union(self, other: SparseBitset) -> SparseBitset:
        """OR: bits set in either."""
        result = SparseBitset()
        all_chunks = set(self._chunks) | set(other._chunks)
        for chunk in all_chunks:
            val = self._chunks.get(chunk, 0) | other._chunks.get(chunk, 0)
            if val:
                result._chunks[chunk] = val
        result._count = sum(bin(v).count('1') for v in result._chunks.values())
        return result

    def intersection(self, other: SparseBitset) -> SparseBitset:
        """AND: bits set in both."""
        result = SparseBitset()
        for chunk in set(self._chunks) & set(other._chunks):
            val = self._chunks[chunk] & other._chunks[chunk]
            if val:
                result._chunks[chunk] = val
        result._count = sum(bin(v).count('1') for v in result._chunks.values())
        return result

    def difference(self, other: SparseBitset) -> SparseBitset:
        """AND NOT: bits in self but not other."""
        result = SparseBitset()
        for chunk, val in self._chunks.items():
            diff = val & ~other._chunks.get(chunk, 0)
            if diff:
                result._chunks[chunk] = diff
        result._count = sum(bin(v).count('1') for v in result._chunks.values())
        return result

    def xor(self, other: SparseBitset) -> SparseBitset:
        """XOR: bits set in one but not both."""
        result = SparseBitset()
        all_chunks = set(self._chunks) | set(other._chunks)
        for chunk in all_chunks:
            val = self._chunks.get(chunk, 0) ^ other._chunks.get(chunk, 0)
            if val:
                result._chunks[chunk] = val
        result._count = sum(bin(v).count('1') for v in result._chunks.values())
        return result

    def memory_bytes(self) -> int:
        """Approximate memory usage (8 bytes per occupied chunk + overhead)."""
        return len(self._chunks) * 16  # 8 bytes key + 8 bytes value


class SparseBitsetService:
    def __init__(self):
        self._bitsets: dict[str, SparseBitset] = {}

    def create(self, name: str) -> SparseBitset:
        bs = SparseBitset()
        self._bitsets[name] = bs
        return bs

    def get(self, name: str) -> SparseBitset | None:
        return self._bitsets.get(name)
