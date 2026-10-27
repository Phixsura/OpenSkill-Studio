"""Token Bucket V2 — advanced rate limiter with burst, overdraft, and priority lanes.

Implements:
- Classic token bucket with configurable capacity and refill rate
- Priority lanes: critical requests bypass limits
- Overdraft: allow temporary negative balance with penalty
- Token reservation (claim tokens for future use)
- Multi-bucket coordination (global + per-endpoint)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time


@dataclass
class Bucket:
    name: str
    capacity: float
    tokens: float
    refill_rate: float  # tokens per second
    last_refill: float = 0.0
    overdraft_limit: float = 0  # how far below 0 we can go
    overdraft_penalty: float = 2.0  # multiplier on next refill wait
    total_allowed: int = 0
    total_denied: int = 0
    total_overdraft: int = 0

    def __post_init__(self):
        if not self.last_refill: self.last_refill = time.time()


class TokenBucketV2Service:
    def __init__(self):
        self._buckets: dict[str, Bucket] = {}
        self._priority_bypass: set[str] = set()  # keys that bypass limits
        self._reservations: dict[str, float] = {}  # reservation_id -> tokens

    def create_bucket(self, name: str, capacity: float, refill_rate: float,
                      overdraft_limit: float = 0) -> Bucket:
        bucket = Bucket(name=name, capacity=capacity, tokens=capacity,
                        refill_rate=refill_rate, overdraft_limit=overdraft_limit)
        self._buckets[name] = bucket
        return bucket

    def _refill(self, bucket: Bucket) -> None:
        now = time.time()
        elapsed = now - bucket.last_refill
        added = elapsed * bucket.refill_rate
        # Overdraft penalty: slower refill when in overdraft
        if bucket.tokens < 0:
            added /= bucket.overdraft_penalty
        bucket.tokens = min(bucket.capacity, bucket.tokens + added)
        bucket.last_refill = now

    def consume(self, bucket_name: str, tokens: float = 1,
                priority: str = "normal") -> dict:
        """Try to consume tokens. Returns allow/deny decision."""
        bucket = self._buckets.get(bucket_name)
        if not bucket:
            return {"allowed": True, "reason": "no bucket configured"}

        # Priority bypass
        if priority == "critical":
            bucket.total_allowed += 1
            return {"allowed": True, "reason": "priority bypass",
                    "remaining": bucket.tokens}

        self._refill(bucket)

        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            bucket.total_allowed += 1
            return {"allowed": True, "remaining": round(bucket.tokens, 2),
                    "capacity": bucket.capacity}

        # Overdraft check
        if bucket.overdraft_limit > 0 and bucket.tokens + tokens >= -bucket.overdraft_limit:
            bucket.tokens -= tokens
            bucket.total_allowed += 1
            bucket.total_overdraft += 1
            return {"allowed": True, "overdraft": True,
                    "remaining": round(bucket.tokens, 2),
                    "penalty": "slower refill until balance restored"}

        # Denied
        bucket.total_denied += 1
        wait_seconds = (tokens - bucket.tokens) / bucket.refill_rate
        return {"allowed": False, "remaining": round(bucket.tokens, 2),
                "retry_after_seconds": round(wait_seconds, 2)}

    def reserve(self, bucket_name: str, tokens: float,
                reservation_id: str) -> bool:
        """Reserve tokens for future use."""
        bucket = self._buckets.get(bucket_name)
        if not bucket:
            return False
        self._refill(bucket)
        if bucket.tokens >= tokens:
            bucket.tokens -= tokens
            self._reservations[reservation_id] = tokens
            return True
        return False

    def cancel_reservation(self, bucket_name: str, reservation_id: str) -> bool:
        """Cancel a reservation, returning tokens to bucket."""
        tokens = self._reservations.pop(reservation_id, 0)
        if not tokens:
            return False
        bucket = self._buckets.get(bucket_name)
        if bucket:
            bucket.tokens = min(bucket.capacity, bucket.tokens + tokens)
        return True

    def multi_bucket_consume(self, bucket_names: list[str],
                              tokens: float = 1) -> dict:
        """Consume from multiple buckets (all must pass)."""
        # Pre-check all buckets
        for name in bucket_names:
            bucket = self._buckets.get(name)
            if not bucket:
                continue
            self._refill(bucket)
            if bucket.tokens < tokens and (bucket.overdraft_limit == 0 or
                                            bucket.tokens <= -bucket.overdraft_limit):
                return {"allowed": False, "blocking_bucket": name}

        # All pass — consume
        for name in bucket_names:
            bucket = self._buckets.get(name)
            if bucket:
                bucket.tokens -= tokens
                bucket.total_allowed += 1

        return {"allowed": True, "buckets_checked": len(bucket_names)}

    def get_stats(self, bucket_name: str) -> dict:
        bucket = self._buckets.get(bucket_name)
        if not bucket:
            return {}
        self._refill(bucket)
        return {
            "name": bucket.name, "tokens": round(bucket.tokens, 2),
            "capacity": bucket.capacity, "refill_rate": bucket.refill_rate,
            "utilization": round((1 - bucket.tokens / bucket.capacity) * 100, 1),
            "total_allowed": bucket.total_allowed,
            "total_denied": bucket.total_denied,
            "total_overdraft": bucket.total_overdraft,
        }
