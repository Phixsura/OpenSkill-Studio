"""App Token Bucket — token bucket rate limiter.

Implements token bucket algorithm:
- Configurable capacity and refill rate
- Consume tokens for requests
- Check remaining tokens
- Per-installation scoped buckets
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class TokenBucket:
    """A token bucket."""

    bucket_id: str
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float
    last_refill: float

    def refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, count: int = 1) -> bool:
        self.refill()
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

    @property
    def available(self) -> int:
        self.refill()
        return int(self.tokens)


class AppTokenBucket:
    """Token bucket rate limiter."""

    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str], TokenBucket] = {}

    def create_bucket(
        self, installation_id: str, bucket_id: str,
        capacity: int = 100, refill_rate: float = 10.0,
    ) -> TokenBucket:
        if not installation_id:
            raise ValueError("installation_id is required")
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive")

        bucket = TokenBucket(
            bucket_id=bucket_id, capacity=capacity,
            refill_rate=refill_rate, tokens=float(capacity),
            last_refill=time.time(),
        )
        self._buckets[(installation_id, bucket_id)] = bucket
        return bucket

    def consume(self, installation_id: str, bucket_id: str, count: int = 1) -> bool:
        b = self._get(installation_id, bucket_id)
        return b.consume(count)

    def available(self, installation_id: str, bucket_id: str) -> int:
        return self._get(installation_id, bucket_id).available

    def reset(self, installation_id: str, bucket_id: str) -> TokenBucket:
        b = self._get(installation_id, bucket_id)
        b.tokens = float(b.capacity)
        b.last_refill = time.time()
        return b

    def list_buckets(self, installation_id: str) -> list[TokenBucket]:
        return [b for (inst, _), b in self._buckets.items() if inst == installation_id]

    def _get(self, installation_id: str, bucket_id: str) -> TokenBucket:
        key = (installation_id, bucket_id)
        b = self._buckets.get(key)
        if b is None:
            raise KeyError(f"Bucket {bucket_id} not found")
        return b
