"""API Rate Limit Token Bucket — token bucket rate limiting algorithm."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class TokenBucket:
    consumer_id: str
    capacity: int  # max tokens
    refill_rate: float  # tokens per second
    tokens: float = 0.0
    last_refill: float = field(default_factory=time.time)

    def _refill(self) -> None:
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now

    def consume(self, count: int = 1) -> bool:
        self._refill()
        if self.tokens >= count:
            self.tokens -= count
            return True
        return False

    @property
    def available(self) -> int:
        self._refill()
        return int(self.tokens)

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiRateLimitTokenBucket:
    def __init__(self) -> None:
        self._buckets: dict[tuple[str, str, str], TokenBucket] = {}

    def configure(self, installation_id: str, consumer_id: str, endpoint: str, capacity: int, refill_rate: float) -> TokenBucket:
        if not installation_id: raise ValueError("installation_id is required")
        if capacity < 1: raise ValueError("capacity must be >= 1")
        if refill_rate <= 0: raise ValueError("refill_rate must be > 0")
        bucket = TokenBucket(consumer_id=consumer_id, capacity=capacity, refill_rate=refill_rate, tokens=float(capacity))
        self._buckets[(installation_id, consumer_id, endpoint)] = bucket
        return bucket

    def try_consume(self, installation_id: str, consumer_id: str, endpoint: str, count: int = 1) -> dict[str, object]:
        bucket = self._buckets.get((installation_id, consumer_id, endpoint))
        if bucket is None: return {"allowed": True, "reason": "no_bucket"}
        if bucket.consume(count):
            return {"allowed": True, "remaining": bucket.available}
        return {"allowed": False, "remaining": 0, "retry_after_s": round(count / bucket.refill_rate, 2)}

    def get_bucket(self, installation_id: str, consumer_id: str, endpoint: str) -> TokenBucket | None:
        return self._buckets.get((installation_id, consumer_id, endpoint))

    def list_buckets(self, installation_id: str) -> list[TokenBucket]:
        return [b for (inst, _, _), b in self._buckets.items() if inst == installation_id]
