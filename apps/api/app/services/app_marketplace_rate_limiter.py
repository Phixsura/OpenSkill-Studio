"""Rate Limiter — token bucket rate limiting for API key access.

Implements a token bucket algorithm to enforce per-key rate limits
on the developer platform API.
"""
from __future__ import annotations
import time
from dataclasses import dataclass, field


@dataclass
class TokenBucket:
    capacity: int
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = field(default_factory=time.monotonic)

    def _refill(self) -> None:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, count: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        self._refill()
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

    def available(self) -> int:
        """Return number of available tokens."""
        self._refill()
        return int(self.tokens)


class RateLimiter:
    """Manages per-key rate limiting using token buckets."""

    def __init__(self, default_capacity: int = 100, default_refill_rate: float = 10.0):
        self._buckets: dict[str, TokenBucket] = {}
        self._default_capacity = default_capacity
        self._default_refill_rate = default_refill_rate
        self._denied_count: dict[str, int] = {}

    def _get_bucket(self, key: str) -> TokenBucket:
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(
                capacity=self._default_capacity,
                tokens=float(self._default_capacity),
                refill_rate=self._default_refill_rate,
            )
        return self._buckets[key]

    def allow(self, key: str, cost: int = 1) -> bool:
        """Check if request is allowed under rate limit."""
        bucket = self._get_bucket(key)
        allowed = bucket.consume(cost)
        if not allowed:
            self._denied_count[key] = self._denied_count.get(key, 0) + 1
        return allowed

    def remaining(self, key: str) -> int:
        """Get remaining tokens for a key."""
        return self._get_bucket(key).available()

    def set_limit(self, key: str, capacity: int, refill_rate: float) -> None:
        """Set custom rate limit for a specific key."""
        self._buckets[key] = TokenBucket(
            capacity=capacity,
            tokens=float(capacity),
            refill_rate=refill_rate,
        )

    def get_stats(self, key: str) -> dict:
        """Get rate limit stats for a key."""
        bucket = self._get_bucket(key)
        return {
            "key": key,
            "capacity": bucket.capacity,
            "remaining": bucket.available(),
            "refill_rate": bucket.refill_rate,
            "denied_count": self._denied_count.get(key, 0),
        }

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        if key in self._buckets:
            self._buckets[key].tokens = float(self._buckets[key].capacity)
            self._buckets[key].last_refill = time.monotonic()
        self._denied_count.pop(key, None)
