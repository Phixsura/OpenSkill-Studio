"""LSM Tree — Log-Structured Merge Tree for write-optimized storage.

The storage engine behind LevelDB, RocksDB, Cassandra.

Implements:
- In-memory memtable (sorted dict) for fast writes
- Flush memtable to immutable sorted run (SSTable)
- Compaction: merge overlapping SSTables
- Read: check memtable first, then SSTables newest to oldest
- Bloom filter per SSTable for negative lookups
- Tombstone-based deletes
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import OrderedDict
import hashlib
import time


TOMBSTONE = object()  # sentinel for deleted keys


@dataclass
class SSTable:
    """Immutable sorted string table."""
    level: int
    data: dict[str, object]  # sorted by key
    bloom_bits: set[str]  # simplified bloom filter
    created_at: float = 0.0
    size: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()
        self.size = len(self.data)

    def get(self, key: str) -> tuple[bool, object]:
        """Returns (found, value). value=TOMBSTONE means deleted."""
        # Bloom filter check first
        if key not in self.bloom_bits:
            return False, None
        if key in self.data:
            return True, self.data[key]
        return False, None  # bloom false positive


class LsmTreeService:
    def __init__(self, memtable_threshold: int = 100):
        self._memtable: dict[str, object] = {}
        self._sstables: list[SSTable] = []  # newest first
        self._memtable_threshold = memtable_threshold
        self._write_count = 0
        self._compaction_count = 0

    def put(self, key: str, value: object) -> None:
        """Write to memtable. Auto-flush when threshold reached."""
        self._memtable[key] = value
        self._write_count += 1
        if len(self._memtable) >= self._memtable_threshold:
            self._flush()

    def get(self, key: str) -> object | None:
        """Read: memtable → SSTables (newest first). Returns None if not found."""
        # Check memtable first (most recent writes)
        if key in self._memtable:
            val = self._memtable[key]
            return None if val is TOMBSTONE else val

        # Check SSTables from newest to oldest
        for sst in self._sstables:
            found, val = sst.get(key)
            if found:
                return None if val is TOMBSTONE else val

        return None

    def delete(self, key: str) -> None:
        """Delete via tombstone marker."""
        self._memtable[key] = TOMBSTONE
        if len(self._memtable) >= self._memtable_threshold:
            self._flush()

    def _flush(self) -> SSTable:
        """Flush memtable to a new SSTable (level 0)."""
        if not self._memtable:
            return None
        # Build bloom filter (simplified: just store keys)
        bloom = set(self._memtable.keys())
        # Sort by key
        sorted_data = dict(sorted(self._memtable.items()))
        sst = SSTable(level=0, data=sorted_data, bloom_bits=bloom)
        self._sstables.insert(0, sst)  # newest first
        self._memtable = {}
        return sst

    def compact(self) -> int:
        """Merge overlapping SSTables at the same level."""
        if len(self._sstables) < 2:
            return 0

        # Simple compaction: merge all level-0 tables into one
        level0 = [s for s in self._sstables if s.level == 0]
        if len(level0) < 2:
            return 0

        merged_data: dict[str, object] = {}
        # Oldest first so newer values overwrite
        for sst in reversed(level0):
            for k, v in sst.data.items():
                merged_data[k] = v

        # Remove tombstones in compacted output
        clean_data = {k: v for k, v in sorted(merged_data.items()) if v is not TOMBSTONE}
        bloom = set(clean_data.keys())
        new_sst = SSTable(level=1, data=clean_data, bloom_bits=bloom)

        # Replace level-0 tables with single level-1 table
        self._sstables = [s for s in self._sstables if s.level != 0]
        self._sstables.insert(0, new_sst)
        self._compaction_count += 1
        return len(level0)

    def force_flush(self) -> None:
        """Manually flush memtable."""
        self._flush()

    def range_scan(self, start: str, end: str) -> list[tuple[str, object]]:
        """Scan keys in [start, end] range across all levels."""
        # Merge all data, newest wins
        merged: dict[str, object] = {}
        for sst in reversed(self._sstables):
            for k, v in sst.data.items():
                if start <= k <= end:
                    merged[k] = v
        # Memtable overwrites
        for k, v in self._memtable.items():
            if start <= k <= end:
                merged[k] = v
        # Filter tombstones
        return [(k, v) for k, v in sorted(merged.items()) if v is not TOMBSTONE]

    def stats(self) -> dict:
        return {
            "memtable_size": len(self._memtable),
            "sstable_count": len(self._sstables),
            "total_entries": sum(s.size for s in self._sstables) + len(self._memtable),
            "total_writes": self._write_count,
            "compactions": self._compaction_count,
            "levels": {s.level: s.size for s in self._sstables},
        }
