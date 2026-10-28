"""App Token Bucket — classic token bucket rate limiter for burst-tolerant endpoints.

Provides token bucket rate limiting complementing the sliding window limiter:
- Configurable bucket capacity and refill rate
- Burst tolerance up to bucket capacity
- Per-key isolated buckets
- Consume N tokens at once
- Current bucket state query
- Auto-refill on access
"""

from __future__ import annotations

import time
from dataclasses import dataclass

import structlog

log = structlog.get_logger()


@dataclass
class BucketState:
    """Current state of a token bucket."""

    tokens: float
    capacity: int
    refill_rate: float    # tokens per second
    last_refill: float    # unix timestamp


@dataclass
class ConsumeResult:
    """Result of attempting to consume tokens."""

    allowed: bool
    tokens_remaining: float
    retry_after_seconds: float   # 0 if allowed


class AppTokenBucket:
    """Token bucket rate limiter with burst support."""

    def __init__(self, capacity: int = 100, refill_rate: float = 10.0):
        """
        capacity: max tokens in the bucket (burst limit).
        refill_rate: tokens added per second.
        """
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        if refill_rate <= 0:
            raise ValueError("Refill rate must be positive")
        self._capacity = capacity
        self._refill_rate = refill_rate
        # key → BucketState
        self._buckets: dict[str, BucketState] = {}

    def _get_or_create(self, key: str, now: float) -> BucketState:
        bucket = self._buckets.get(key)
        if bucket is None:
            bucket = BucketState(
                tokens=float(self._capacity),
                capacity=self._capacity,
                refill_rate=self._refill_rate,
                last_refill=now,
            )
            self._buckets[key] = bucket
        return bucket

    def _refill(self, bucket: BucketState, now: float) -> None:
        elapsed = now - bucket.last_refill
        if elapsed > 0:
            bucket.tokens = min(
                bucket.capacity,
                bucket.tokens + elapsed * bucket.refill_rate,
            )
            bucket.last_refill = now

    def consume(self, key: str, tokens: int = 1,
                now: float | None = None) -> ConsumeResult:
        """Try to consume tokens from a bucket.

        Returns allowed=True if sufficient tokens available.
        """
        if tokens <= 0:
            raise ValueError("Tokens must be positive")
        now = now or time.time()
        bucket = self._get_or_create(key, now)
        self._refill(bucket, now)

        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            return ConsumeResult(
                allowed=True,
                tokens_remaining=bucket.tokens,
                retry_after_seconds=0,
            )

        # Not enough tokens — compute wait time
        deficit = tokens - bucket.tokens
        retry_after = deficit / bucket.refill_rate
        return ConsumeResult(
            allowed=False,
            tokens_remaining=bucket.tokens,
            retry_after_seconds=round(retry_after, 3),
        )

    def peek(self, key: str, now: float | None = None) -> BucketState:
        """Get current bucket state without consuming."""
        now = now or time.time()
        bucket = self._get_or_create(key, now)
        self._refill(bucket, now)
        return bucket

    def reset(self, key: str) -> None:
        """Reset a bucket to full capacity."""
        self._buckets.pop(key, None)
