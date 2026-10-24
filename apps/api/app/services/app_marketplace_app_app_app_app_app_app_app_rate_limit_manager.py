"""API rate limit manager — track and enforce per-key rate limits."""
from __future__ import annotations
import time


class RateLimitManager:
    def __init__(self):
        self._buckets: dict[str, dict] = {}

    def configure(self, key: str, *, limit: int = 100, window_sec: int = 60) -> dict:
        self._buckets[key] = {"limit": limit, "window": window_sec, "hits": [], "blocked": 0}
        return {"key": key, "limit": limit, "window": window_sec, "status": "configured"}

    def check(self, key: str, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.monotonic()
        bucket = self._buckets.get(key)
        if not bucket:
            return {"allowed": False, "reason": "unconfigured", "key": key}
        window = bucket["window"]
        bucket["hits"] = [t for t in bucket["hits"] if ts - t < window]
        remaining = bucket["limit"] - len(bucket["hits"])
        if remaining <= 0:
            bucket["blocked"] += 1
            retry_after = round(bucket["hits"][0] + window - ts, 1)
            return {"allowed": False, "reason": "rate_limited", "key": key,
                    "remaining": 0, "retry_after": max(retry_after, 0.1)}
        bucket["hits"].append(ts)
        return {"allowed": True, "key": key, "remaining": remaining - 1,
                "limit": bucket["limit"], "window": window}

    def stats(self, key: str) -> dict:
        b = self._buckets.get(key, {})
        return {"key": key, "total_hits": len(b.get("hits", [])),
                "blocked": b.get("blocked", 0), "limit": b.get("limit", 0)}
