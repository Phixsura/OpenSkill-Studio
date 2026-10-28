"""App Idempotency Store — prevent duplicate API request processing.

Ensures app API requests with the same idempotency key are only processed once:
- Store request results keyed by idempotency key
- TTL-based expiry (default 24h)
- Collision detection (same key, different payload hash)
- Per-installation scoped keys
- Replay stored response on duplicate
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta

import structlog

log = structlog.get_logger()

DEFAULT_TTL_HOURS = 24


@dataclass
class IdempotencyEntry:
    """A stored idempotency result."""

    key: str
    installation_id: str
    payload_hash: str
    status_code: int
    response_body: dict
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime = field(default_factory=lambda: datetime.now(UTC) + timedelta(hours=DEFAULT_TTL_HOURS))


@dataclass
class IdempotencyCheckResult:
    """Result of checking an idempotency key."""

    is_duplicate: bool
    stored_response: dict | None = None
    stored_status_code: int | None = None
    is_collision: bool = False      # same key, different payload
    error: str | None = None


def _hash_payload(payload: dict) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(canonical.encode()).hexdigest()[:16]


class AppIdempotencyStore:
    """Prevent duplicate API request processing."""

    def __init__(self, ttl_hours: int = DEFAULT_TTL_HOURS):
        self._ttl_hours = ttl_hours
        # (installation_id, key) → IdempotencyEntry
        self._entries: dict[tuple[str, str], IdempotencyEntry] = {}

    def check(self, installation_id: str, key: str,
              payload: dict, now: datetime | None = None) -> IdempotencyCheckResult:
        """Check if a request with this key has already been processed."""
        if not key:
            return IdempotencyCheckResult(is_duplicate=False)

        now = now or datetime.now(UTC)
        compound = (installation_id, key)
        entry = self._entries.get(compound)

        if entry is None:
            return IdempotencyCheckResult(is_duplicate=False)

        # Expired
        if now >= entry.expires_at:
            del self._entries[compound]
            return IdempotencyCheckResult(is_duplicate=False)

        # Collision check: same key but different payload
        payload_hash = _hash_payload(payload)
        if payload_hash != entry.payload_hash:
            return IdempotencyCheckResult(
                is_duplicate=True, is_collision=True,
                error="Idempotency key reused with different payload",
            )

        # Genuine duplicate — replay stored response
        return IdempotencyCheckResult(
            is_duplicate=True,
            stored_response=entry.response_body,
            stored_status_code=entry.status_code,
        )

    def store(self, installation_id: str, key: str, payload: dict,
              status_code: int, response_body: dict) -> IdempotencyEntry:
        """Store a processed request result."""
        if not key:
            raise ValueError("Idempotency key is required")

        now = datetime.now(UTC)
        entry = IdempotencyEntry(
            key=key, installation_id=installation_id,
            payload_hash=_hash_payload(payload),
            status_code=status_code, response_body=response_body,
            created_at=now,
            expires_at=now + timedelta(hours=self._ttl_hours),
        )
        self._entries[(installation_id, key)] = entry
        return entry

    def cleanup_expired(self, now: datetime | None = None) -> int:
        """Remove expired entries. Returns count removed."""
        now = now or datetime.now(UTC)
        expired = [k for k, v in self._entries.items() if now >= v.expires_at]
        for k in expired:
            del self._entries[k]
        return len(expired)

    def size(self) -> int:
        return len(self._entries)
