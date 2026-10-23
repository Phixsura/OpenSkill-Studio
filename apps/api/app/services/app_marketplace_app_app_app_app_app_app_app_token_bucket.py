"""Token bucket rate limiter — smooth rate limiting with burst support."""
from __future__ import annotations


class TokenBucket:
    def __init__(self, *, capacity: int, refill_rate: float):
        self._capacity = capacity
        self._refill_rate = refill_rate  # tokens per second
        self._tokens = float(capacity)
        self._last_refill = 0.0

    def consume(self, *, tokens: int = 1, now: float = 0) -> dict:
        self._refill(now)
        if self._tokens >= tokens:
            self._tokens -= tokens
            return {"allowed": True, "remaining": int(self._tokens),
                    "capacity": self._capacity}
        wait = (tokens - self._tokens) / self._refill_rate
        return {"allowed": False, "remaining": int(self._tokens),
                "retry_after_sec": round(wait, 2)}

    def status(self, *, now: float = 0) -> dict:
        self._refill(now)
        pct = round(self._tokens / self._capacity * 100, 1)
        return {"tokens": int(self._tokens), "capacity": self._capacity,
                "refill_rate": self._refill_rate, "fill_pct": pct}

    def _refill(self, now: float) -> None:
        elapsed = now - self._last_refill
        if elapsed > 0:
            self._tokens = min(self._capacity, self._tokens + elapsed * self._refill_rate)
            self._last_refill = now
