"""Token bucket rate limiter — classic token bucket algorithm."""
from __future__ import annotations


class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._buckets: dict[str, dict] = {}

    def _get(self, key: str, now: float) -> dict:
        if key not in self._buckets:
            self._buckets[key] = {"tokens": float(self.capacity), "last_refill": now}
        b = self._buckets[key]
        elapsed = now - b["last_refill"]
        b["tokens"] = min(self.capacity, b["tokens"] + elapsed * self.refill_rate)
        b["last_refill"] = now
        return b

    def consume(self, key: str, tokens: int = 1, now: float = 0) -> dict:
        b = self._get(key, now)
        if b["tokens"] >= tokens:
            b["tokens"] -= tokens
            return {"allowed": True, "remaining": int(b["tokens"]),
                    "capacity": self.capacity}
        wait = round((tokens - b["tokens"]) / self.refill_rate, 2)
        return {"allowed": False, "remaining": int(b["tokens"]),
                "capacity": self.capacity, "retry_after_seconds": wait}

    def peek(self, key: str, now: float = 0) -> dict:
        b = self._get(key, now)
        return {"tokens": int(b["tokens"]), "capacity": self.capacity,
                "pct_full": round(b["tokens"] / self.capacity * 100, 1)}
