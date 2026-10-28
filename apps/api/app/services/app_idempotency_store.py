"""App Idempotency Store — prevent duplicate request processing.

Manages idempotency keys:
- Store request results by idempotency key
- Return cached result for duplicate requests
- TTL-based key expiration
- Per-installation scoped keys
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class IdempotencyEntry:
    """A stored idempotency entry."""

    key: str
    status_code: int
    response_body: str
    created_at: float = field(default_factory=time.time)
    ttl_seconds: int = 86400  # 24h default

    @property
    def is_expired(self) -> bool:
        return (time.time() - self.created_at) > self.ttl_seconds


class AppIdempotencyStore:
    """Prevent duplicate request processing."""

    def __init__(self, default_ttl: int = 86400) -> None:
        self._default_ttl = default_ttl
        self._store: dict[tuple[str, str], IdempotencyEntry] = {}

    def check(self, installation_id: str, key: str) -> IdempotencyEntry | None:
        """Check if key exists and is not expired."""
        if not key:
            return None
        entry = self._store.get((installation_id, key))
        if entry is None:
            return None
        if entry.is_expired:
            del self._store[(installation_id, key)]
            return None
        return entry

    def store(
        self, installation_id: str, key: str,
        status_code: int, response_body: str,
        ttl_seconds: int | None = None,
    ) -> IdempotencyEntry:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key:
            raise ValueError("key is required")

        # Don't overwrite existing non-expired entry
        existing = self.check(installation_id, key)
        if existing is not None:
            raise ValueError(f"Key {key} already exists")

        entry = IdempotencyEntry(
            key=key, status_code=status_code,
            response_body=response_body,
            ttl_seconds=ttl_seconds or self._default_ttl,
        )
        self._store[(installation_id, key)] = entry
        return entry

    def remove(self, installation_id: str, key: str) -> bool:
        k = (installation_id, key)
        if k in self._store:
            del self._store[k]
            return True
        return False

    def cleanup_expired(self, installation_id: str) -> int:
        """Remove expired entries. Returns count removed."""
        to_remove = [
            k for k, v in self._store.items()
            if k[0] == installation_id and v.is_expired
        ]
        for k in to_remove:
            del self._store[k]
        return len(to_remove)

    def count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._store if inst == installation_id)
