"""App API Developer API Rate Limit Override — per-consumer rate limit exceptions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitOverride:
    override_id: str
    consumer_id: str
    endpoint: str  # "*" for all endpoints
    limit_per_minute: int
    reason: str
    expires_at: float | None = None
    created_at: float = field(default_factory=time.time)

    @property
    def expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class AppAPIDeveloperAPIApiRateLimitOverride:
    def __init__(self) -> None:
        self._overrides: dict[tuple[str, str], RateLimitOverride] = {}

    def create(self, installation_id: str, override_id: str, consumer_id: str, endpoint: str, limit_per_minute: int, reason: str, expires_at: float | None = None) -> RateLimitOverride:
        if not installation_id: raise ValueError("installation_id is required")
        if limit_per_minute <= 0: raise ValueError("limit must be positive")
        key = (installation_id, override_id)
        if key in self._overrides: raise ValueError(f"Override {override_id} exists")
        o = RateLimitOverride(override_id=override_id, consumer_id=consumer_id, endpoint=endpoint, limit_per_minute=limit_per_minute, reason=reason, expires_at=expires_at)
        self._overrides[key] = o
        return o

    def effective_limit(self, installation_id: str, consumer_id: str, endpoint: str, default_limit: int) -> int:
        for (inst, _), o in self._overrides.items():
            if inst == installation_id and o.consumer_id == consumer_id and not o.expired:
                if o.endpoint == "*" or o.endpoint == endpoint:
                    return o.limit_per_minute
        return default_limit

    def active(self, installation_id: str) -> list[RateLimitOverride]:
        return [o for (inst, _), o in self._overrides.items() if inst == installation_id and not o.expired]

    def revoke(self, installation_id: str, override_id: str) -> bool:
        key = (installation_id, override_id)
        if key in self._overrides:
            self._overrides[key].expires_at = time.time() - 1
            return True
        return False
