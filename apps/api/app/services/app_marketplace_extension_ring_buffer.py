"""Ring Buffer — fixed-size circular buffer for bounded event streaming.

Implements:
- O(1) write (append) and O(1) read (consume)
- Overwrite-oldest on full (configurable: overwrite or reject)
- Batch read/write
- Consumer groups with independent read positions
- Watermark tracking (high/low for backpressure signaling)
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class RingBufferEntry:
    sequence: int
    data: object
    timestamp: float = 0.0


class RingBufferService:
    def __init__(self, capacity: int = 1024, overwrite: bool = True):
        if capacity < 1:
            raise ValueError("Capacity must be >= 1")
        self._capacity = capacity
        self._buffer: list[RingBufferEntry | None] = [None] * capacity
        self._write_pos = 0  # next write position (sequence number)
        self._overwrite = overwrite
        self._consumers: dict[str, int] = {}  # consumer_id -> last read sequence
        self._high_watermark = int(capacity * 0.9)
        self._low_watermark = int(capacity * 0.5)

    def write(self, data: object) -> int:
        """Write one entry. Returns sequence number."""
        import time
        if not self._overwrite and self._is_full():
            raise BufferError("Ring buffer full")

        seq = self._write_pos
        idx = seq % self._capacity
        self._buffer[idx] = RingBufferEntry(
            sequence=seq, data=data, timestamp=time.time())
        self._write_pos += 1
        return seq

    def write_batch(self, items: list) -> list[int]:
        """Write multiple entries. Returns list of sequence numbers."""
        return [self.write(item) for item in items]

    def read(self, consumer_id: str, count: int = 1) -> list[RingBufferEntry]:
        """Read up to `count` entries for a consumer. Advances position."""
        if consumer_id not in self._consumers:
            # Start from oldest available
            oldest = max(0, self._write_pos - self._capacity)
            self._consumers[consumer_id] = oldest

        start = self._consumers[consumer_id]
        available = self._write_pos - start
        to_read = min(count, available)

        entries = []
        for i in range(to_read):
            seq = start + i
            idx = seq % self._capacity
            entry = self._buffer[idx]
            if entry and entry.sequence == seq:
                entries.append(entry)
            # else: overwritten, skip

        self._consumers[consumer_id] = start + to_read
        return entries

    def peek(self, consumer_id: str, count: int = 1) -> list[RingBufferEntry]:
        """Peek without advancing position."""
        if consumer_id not in self._consumers:
            oldest = max(0, self._write_pos - self._capacity)
            self._consumers[consumer_id] = oldest

        start = self._consumers[consumer_id]
        available = self._write_pos - start
        to_read = min(count, available)

        entries = []
        for i in range(to_read):
            seq = start + i
            idx = seq % self._capacity
            entry = self._buffer[idx]
            if entry and entry.sequence == seq:
                entries.append(entry)
        return entries

    def commit(self, consumer_id: str, sequence: int) -> None:
        """Explicitly advance consumer to a specific position."""
        self._consumers[consumer_id] = sequence + 1

    def _is_full(self) -> bool:
        # Check if oldest consumer is about to be overwritten
        if not self._consumers:
            return self._write_pos >= self._capacity
        oldest_consumer = min(self._consumers.values())
        return self._write_pos - oldest_consumer >= self._capacity

    def backpressure_status(self) -> str:
        """Return 'ok', 'warning', or 'critical' based on fill level."""
        fill = self._write_pos % self._capacity if self._write_pos < self._capacity else self._capacity
        used = self._used_slots()
        if used >= self._high_watermark:
            return "critical"
        if used >= self._low_watermark:
            return "warning"
        return "ok"

    def _used_slots(self) -> int:
        if not self._consumers:
            return min(self._write_pos, self._capacity)
        oldest = min(self._consumers.values())
        return self._write_pos - oldest

    def stats(self) -> dict:
        return {
            "capacity": self._capacity,
            "total_written": self._write_pos,
            "used_slots": self._used_slots(),
            "consumers": len(self._consumers),
            "backpressure": self.backpressure_status(),
            "consumer_lag": {cid: self._write_pos - pos
                             for cid, pos in self._consumers.items()},
        }
