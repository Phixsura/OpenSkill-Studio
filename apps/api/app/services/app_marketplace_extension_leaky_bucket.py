"""Leaky Bucket Queue — smooth traffic shaping with constant drain rate.

Unlike token bucket (allows bursts), leaky bucket enforces a constant
output rate. Requests queue up and drain at fixed intervals.

Implements:
- Fixed drain rate (requests per second)
- Queue with configurable depth (burst buffer)
- Overflow rejection when queue full
- Drain simulation for testing
- Per-key independent buckets
"""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class LeakyBucketState:
    key: str
    queue: deque = field(default_factory=deque)
    drain_rate: float = 10.0  # requests per second
    max_queue: int = 100
    last_drain: float = 0.0
    total_accepted: int = 0
    total_rejected: int = 0
    total_drained: int = 0


class LeakyBucketService:
    def __init__(self):
        self._buckets: dict[str, LeakyBucketState] = {}

    def configure(self, key: str, drain_rate: float = 10.0,
                  max_queue: int = 100) -> LeakyBucketState:
        bucket = LeakyBucketState(key=key, drain_rate=drain_rate,
                                  max_queue=max_queue, last_drain=time.time())
        self._buckets[key] = bucket
        return bucket

    def submit(self, key: str, request_id: str = "") -> dict:
        """Submit a request. Returns accept/reject decision."""
        bucket = self._buckets.get(key)
        if not bucket:
            bucket = self.configure(key)

        # Drain based on elapsed time
        self._drain(bucket)

        if len(bucket.queue) >= bucket.max_queue:
            bucket.total_rejected += 1
            return {
                "accepted": False,
                "queue_depth": len(bucket.queue),
                "max_queue": bucket.max_queue,
                "retry_after": round(1.0 / bucket.drain_rate, 3),
            }

        bucket.queue.append({"id": request_id or f"r-{bucket.total_accepted}",
                             "submitted_at": time.time()})
        bucket.total_accepted += 1
        return {
            "accepted": True,
            "queue_position": len(bucket.queue),
            "estimated_wait_ms": round(len(bucket.queue) / bucket.drain_rate * 1000, 1),
        }

    def _drain(self, bucket: LeakyBucketState) -> int:
        """Drain requests based on elapsed time since last drain."""
        now = time.time()
        elapsed = now - bucket.last_drain
        to_drain = int(elapsed * bucket.drain_rate)

        if to_drain <= 0:
            return 0

        drained = min(to_drain, len(bucket.queue))
        for _ in range(drained):
            bucket.queue.popleft()
            bucket.total_drained += 1

        bucket.last_drain = now
        return drained

    def drain_one(self, key: str) -> dict | None:
        """Manually drain one request (for testing/processing)."""
        bucket = self._buckets.get(key)
        if not bucket or not bucket.queue:
            return None
        item = bucket.queue.popleft()
        bucket.total_drained += 1
        return item

    def get_queue_depth(self, key: str) -> int:
        bucket = self._buckets.get(key)
        if not bucket:
            return 0
        self._drain(bucket)
        return len(bucket.queue)

    def stats(self, key: str) -> dict:
        bucket = self._buckets.get(key)
        if not bucket:
            return {}
        self._drain(bucket)
        return {
            "queue_depth": len(bucket.queue),
            "drain_rate": bucket.drain_rate,
            "max_queue": bucket.max_queue,
            "total_accepted": bucket.total_accepted,
            "total_rejected": bucket.total_rejected,
            "total_drained": bucket.total_drained,
            "utilization": round(len(bucket.queue) / bucket.max_queue * 100, 1),
        }
