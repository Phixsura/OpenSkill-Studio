"""Idempotency — ensure API operations are safely retryable.

Tracks idempotency keys to prevent duplicate processing of the same
request, with configurable TTL and response caching.
"""
from __future__ import annotations
import time
from dataclasses import dataclass
from copy import deepcopy


@dataclass
class IdempotencyRecord:
    key: str
    response: dict
    status_code: int
    created_at: float
    ttl_seconds: float

    @property
    def expired(self) -> bool:
        return time.monotonic() - self.created_at > self.ttl_seconds


class IdempotencyService:
    """Ensures API operations are safely retryable via idempotency keys."""

    def __init__(self, default_ttl: float = 86400.0):
        self._records: dict[str, IdempotencyRecord] = {}
        self._default_ttl = default_ttl

    def check(self, key: str) -> tuple[bool, dict | None, int]:
        """Check if key was seen before. Returns (is_duplicate, cached_response, status_code)."""
        record = self._records.get(key)
        if record and not record.expired:
            return True, deepcopy(record.response), record.status_code
        if record and record.expired:
            del self._records[key]
        return False, None, 0

    def record(self, key: str, response: dict, status_code: int,
               ttl: float | None = None) -> None:
        """Record a completed request for future dedup."""
        self._records[key] = IdempotencyRecord(
            key=key, response=deepcopy(response), status_code=status_code,
            created_at=time.monotonic(), ttl_seconds=ttl or self._default_ttl,
        )

    def execute_once(self, key: str, fn: callable,
                     ttl: float | None = None) -> tuple[dict, int, bool]:
        """Execute fn only if key hasn't been seen. Returns (response, status, was_cached)."""
        is_dup, cached, code = self.check(key)
        if is_dup and cached is not None:
            return cached, code, True
        response, status = fn()
        self.record(key, response, status, ttl)
        return response, status, False

    def invalidate(self, key: str) -> bool:
        return self._records.pop(key, None) is not None

    def cleanup_expired(self) -> int:
        expired = [k for k, r in self._records.items() if r.expired]
        for k in expired:
            del self._records[k]
        return len(expired)

    def stats(self) -> dict:
        total = len(self._records)
        expired = sum(1 for r in self._records.values() if r.expired)
        return {"total": total, "active": total - expired, "expired": expired}
