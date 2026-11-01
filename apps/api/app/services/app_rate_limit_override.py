"""App Rate Limit Override — per-consumer rate limit exceptions.

Manages rate limit overrides:
- Grant temporary or permanent overrides
- Override by consumer, endpoint, or globally
- Track override usage
- Per-installation scoped overrides
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class RateLimitOverride:
    """A rate limit override."""

    override_id: str
    consumer_id: str
    limit: int  # requests per minute
    reason: str = ""
    expires_at: float | None = None
    created_at: float = field(default_factory=time.time)
    request_count: int = 0

    @property
    def is_active(self) -> bool:
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True


class AppRateLimitOverride:
    """Manage per-consumer rate limit exceptions."""

    def __init__(self) -> None:
        self._overrides: dict[tuple[str, str], RateLimitOverride] = {}

    def grant(
        self, installation_id: str, override_id: str, consumer_id: str,
        limit: int, reason: str = "", ttl_seconds: int | None = None,
    ) -> RateLimitOverride:
        if not installation_id:
            raise ValueError("installation_id is required")
        if limit < 1:
            raise ValueError("limit must be at least 1")

        expires_at = None
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be positive")
            expires_at = time.time() + ttl_seconds

        override = RateLimitOverride(
            override_id=override_id, consumer_id=consumer_id,
            limit=limit, reason=reason, expires_at=expires_at,
        )
        self._overrides[(installation_id, override_id)] = override
        return override

    def get_override(self, installation_id: str, consumer_id: str) -> RateLimitOverride | None:
        """Get active override for consumer."""
        for (inst, _), o in self._overrides.items():
            if inst == installation_id and o.consumer_id == consumer_id and o.is_active:
                return o
        return None

    def record_usage(self, installation_id: str, override_id: str) -> RateLimitOverride:
        key = (installation_id, override_id)
        o = self._overrides.get(key)
        if o is None:
            raise KeyError(f"Override {override_id} not found")
        o.request_count += 1
        return o

    def revoke(self, installation_id: str, override_id: str) -> RateLimitOverride:
        key = (installation_id, override_id)
        o = self._overrides.get(key)
        if o is None:
            raise KeyError(f"Override {override_id} not found")
        o.expires_at = time.time() - 1  # expire immediately
        return o

    def list_overrides(self, installation_id: str, active_only: bool = False) -> list[RateLimitOverride]:
        overrides = [o for (inst, _), o in self._overrides.items() if inst == installation_id]
        if active_only:
            overrides = [o for o in overrides if o.is_active]
        return overrides
