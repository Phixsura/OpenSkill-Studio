"""Rate limiter — token bucket algorithm for API rate limiting."""

import time
import hashlib


class TokenBucket:
    def __init__(self, *, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self._tokens: dict[str, float] = {}
        self._last_refill: dict[str, float] = {}

    def _refill(self, key: str, now: float) -> float:
        last = self._last_refill.get(key, now)
        tokens = self._tokens.get(key, float(self.capacity))
        elapsed = now - last
        tokens = min(self.capacity, tokens + elapsed * self.refill_rate)
        self._tokens[key] = tokens
        self._last_refill[key] = now
        return tokens

    def consume(self, key: str, tokens: int = 1, now: float | None = None) -> dict:
        t = now if now is not None else time.monotonic()
        available = self._refill(key, t)
        if available >= tokens:
            self._tokens[key] = available - tokens
            return {"allowed": True, "remaining": int(self._tokens[key]),
                    "limit": self.capacity}
        retry_after = (tokens - available) / self.refill_rate
        return {"allowed": False, "remaining": 0, "limit": self.capacity,
                "retry_after_s": round(retry_after, 2)}


def hash_client_key(*, ip: str, api_key: str | None = None) -> str:
    raw = api_key or ip
    return hashlib.sha256(raw.encode()).hexdigest()[:16]
