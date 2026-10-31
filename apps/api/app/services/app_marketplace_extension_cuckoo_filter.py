"""Cuckoo Filter — space-efficient probabilistic set with deletion support.

Unlike Bloom filters, Cuckoo filters support deletion. Uses cuckoo
hashing with fingerprint storage and bucket-based displacement.

Implements:
- Add with cuckoo displacement on collision
- Lookup with fingerprint matching
- Delete (Bloom filters can't do this!)
- Configurable bucket size and fingerprint length
- Load factor tracking
"""
from __future__ import annotations
import hashlib
import random


class CuckooFilterFull(Exception):
    pass


class CuckooFilterService:
    MAX_KICKS = 500

    def __init__(self, capacity: int = 1024, bucket_size: int = 4,
                 fingerprint_bits: int = 8):
        self._capacity = capacity  # number of buckets
        self._bucket_size = bucket_size
        self._fp_bits = fingerprint_bits
        self._fp_mask = (1 << fingerprint_bits) - 1
        self._buckets: list[list[int]] = [[] for _ in range(capacity)]
        self._count = 0

    def _fingerprint(self, item: str) -> int:
        h = int(hashlib.sha256(item.encode()).hexdigest(), 16)
        fp = h & self._fp_mask
        return fp if fp != 0 else 1  # fingerprint must be non-zero

    def _hash1(self, item: str) -> int:
        h = int(hashlib.md5(item.encode()).hexdigest(), 16)
        return h % self._capacity

    def _hash2(self, i1: int, fingerprint: int) -> int:
        """Partial-key cuckoo hashing: i2 = i1 XOR hash(fp)."""
        h = int(hashlib.md5(str(fingerprint).encode()).hexdigest(), 16)
        return (i1 ^ h) % self._capacity

    def add(self, item: str) -> bool:
        """Add item. Returns True if added, raises CuckooFilterFull if table is full."""
        fp = self._fingerprint(item)
        i1 = self._hash1(item)
        i2 = self._hash2(i1, fp)

        # Try primary bucket
        if len(self._buckets[i1]) < self._bucket_size:
            self._buckets[i1].append(fp)
            self._count += 1
            return True

        # Try alternate bucket
        if len(self._buckets[i2]) < self._bucket_size:
            self._buckets[i2].append(fp)
            self._count += 1
            return True

        # Both full — cuckoo displacement
        i = random.choice([i1, i2])
        for _ in range(self.MAX_KICKS):
            # Evict random entry from bucket
            j = random.randrange(len(self._buckets[i]))
            fp, self._buckets[i][j] = self._buckets[i][j], fp
            # Find alternate bucket for evicted fingerprint
            i = self._hash2(i, fp)
            if len(self._buckets[i]) < self._bucket_size:
                self._buckets[i].append(fp)
                self._count += 1
                return True

        raise CuckooFilterFull("Filter is full — too many displacements")

    def contains(self, item: str) -> bool:
        """Check if item might be in the set."""
        fp = self._fingerprint(item)
        i1 = self._hash1(item)
        i2 = self._hash2(i1, fp)
        return fp in self._buckets[i1] or fp in self._buckets[i2]

    def delete(self, item: str) -> bool:
        """Delete item. Returns True if found and removed."""
        fp = self._fingerprint(item)
        i1 = self._hash1(item)
        i2 = self._hash2(i1, fp)

        if fp in self._buckets[i1]:
            self._buckets[i1].remove(fp)
            self._count -= 1
            return True
        if fp in self._buckets[i2]:
            self._buckets[i2].remove(fp)
            self._count -= 1
            return True
        return False

    @property
    def size(self) -> int:
        return self._count

    @property
    def load_factor(self) -> float:
        total_slots = self._capacity * self._bucket_size
        return round(self._count / total_slots, 4) if total_slots else 0

    def stats(self) -> dict:
        total_slots = self._capacity * self._bucket_size
        return {
            "count": self._count,
            "capacity_buckets": self._capacity,
            "bucket_size": self._bucket_size,
            "total_slots": total_slots,
            "load_factor": self.load_factor,
            "fingerprint_bits": self._fp_bits,
            "memory_estimate_bytes": self._capacity * self._bucket_size * (self._fp_bits // 8 + 1),
        }
