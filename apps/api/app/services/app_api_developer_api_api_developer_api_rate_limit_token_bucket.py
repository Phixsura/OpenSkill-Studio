"""App API Developer Rate Limit Token Bucket — token bucket algorithm rate limiting."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class TokenBucket:
    consumer_id: str
    capacity: int
    refill_rate: float  # tokens per second
    tokens: float = 0.0
    last_refill_at: float = field(default_factory=time.time)

    def refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill_at
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill_at = now

    def consume(self, count: int = 1) -> bool:
        self.refill()
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

    @property
    def fill_pct(self) -> float:
        self.refill()
        return round(self.tokens / self.capacity * 100, 1) if self.capacity > 0 else 0.0

class AppAPIDeveloperAPIApiDeveloperApiRateLimitTokenBucket:
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str, str], TokenBucket] = {}

    def configure(self, installation_id: str, consumer_id: str, endpoint: str, capacity: int, refill_rate: float) -> TokenBucket:
        if not installation_id: raise ValueError("installation_id is required")
        if capacity < 1: raise ValueError("capacity must be >= 1")
        if refill_rate <= 0: raise ValueError("refill_rate must be positive")
        key = (installation_id, consumer_id, endpoint)
        b = TokenBucket(consumer_id=consumer_id, capacity=capacity, refill_rate=refill_rate, tokens=float(capacity))
        self._buckets[key] = b
        return b

    def try_consume(self, installation_id: str, consumer_id: str, endpoint: str, count: int = 1) -> tuple[bool, float]:
        key = (installation_id, consumer_id, endpoint)
        b = self._buckets.get(key)
        if b is None: return (True, -1)
        allowed = b.consume(count)
        return (allowed, round(b.tokens, 1))

    def get_bucket(self, installation_id: str, consumer_id: str, endpoint: str) -> TokenBucket | None:
        return self._buckets.get((installation_id, consumer_id, endpoint))

    def all_buckets(self, installation_id: str) -> list[TokenBucket]:
        return [b for (inst, _, _), b in self._buckets.items() if inst == installation_id]
