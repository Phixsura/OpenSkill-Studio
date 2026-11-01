"""Smart Rate Limiter — token bucket with sliding window and adaptive penalties.

Implements a proper token bucket algorithm with:
- Configurable refill rate and burst capacity
- Sliding window tracking for per-minute/hour stats
- Adaptive penalty: repeated limit hits increase cooldown exponentially
- IP-level and API-key-level enforcement
- Retry-After header calculation
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import math


@dataclass
class TokenBucket:
    capacity: int
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = 0.0
    violations: int = 0
    penalty_until: float = 0.0

    def __post_init__(self):
        if not self.last_refill:
            self.last_refill = time.time()
        if self.tokens < 0:
            self.tokens = 0

    def refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def try_consume(self, cost: int = 1) -> tuple[bool, float]:
        """Returns (allowed, retry_after_seconds)."""
        now = time.time()
        # Check penalty cooldown
        if self.penalty_until > now:
            return False, self.penalty_until - now

        self.refill()

        if self.tokens >= cost:
            self.tokens -= cost
            # Decay violations on successful requests
            if self.violations > 0 and now - self.penalty_until > 60:
                self.violations = max(0, self.violations - 1)
            return True, 0.0

        # Rate limited — apply exponential backoff penalty
        self.violations += 1
        penalty_seconds = min(300, 2 ** self.violations)  # max 5 min
        self.penalty_until = now + penalty_seconds
        wait = max((cost - self.tokens) / self.refill_rate, penalty_seconds)
        return False, round(wait, 1)


@dataclass
class SlidingWindowEntry:
    timestamp: float
    count: int


class SmartRateLimiterService:
    def __init__(self):
        self._buckets: dict[str, TokenBucket] = {}
        self._window: dict[str, list[SlidingWindowEntry]] = {}

    def get_or_create(self, key: str, capacity: int = 100,
                      refill_rate: float = 10.0) -> TokenBucket:
        if key not in self._buckets:
            self._buckets[key] = TokenBucket(
                capacity=capacity, tokens=float(capacity),
                refill_rate=refill_rate)
        return self._buckets[key]

    def check(self, key: str, cost: int = 1, capacity: int = 100,
              refill_rate: float = 10.0) -> dict:
        bucket = self.get_or_create(key, capacity, refill_rate)
        allowed, retry_after = bucket.try_consume(cost)

        # Track in sliding window
        now = time.time()
        if key not in self._window:
            self._window[key] = []
        self._window[key].append(SlidingWindowEntry(timestamp=now, count=cost))
        # Prune entries older than 1 hour
        cutoff = now - 3600
        self._window[key] = [e for e in self._window[key] if e.timestamp > cutoff]

        return {
            "allowed": allowed,
            "remaining": max(0, int(bucket.tokens)),
            "limit": bucket.capacity,
            "retry_after": retry_after,
            "violations": bucket.violations,
            "requests_last_minute": self._count_window(key, 60),
            "requests_last_hour": self._count_window(key, 3600),
        }

    def _count_window(self, key: str, seconds: int) -> int:
        cutoff = time.time() - seconds
        return sum(e.count for e in self._window.get(key, []) if e.timestamp > cutoff)

    def reset(self, key: str) -> bool:
        if key in self._buckets:
            b = self._buckets[key]
            b.tokens = float(b.capacity)
            b.violations = 0
            b.penalty_until = 0.0
            return True
        return False

    def get_top_consumers(self, limit: int = 10) -> list[tuple[str, int]]:
        counts = [(k, self._count_window(k, 3600)) for k in self._window]
        return sorted(counts, key=lambda x: x[1], reverse=True)[:limit]
