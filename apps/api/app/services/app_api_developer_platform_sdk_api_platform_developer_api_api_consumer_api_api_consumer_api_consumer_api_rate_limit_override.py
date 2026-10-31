"""Consumer API Rate Limit Override — temporary rate limit adjustments per consumer."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitOverride:
    override_id: str
    consumer_id: str
    endpoint_path: str | None = None  # None = applies to all endpoints
    multiplier: float = 1.0  # 2.0 = double the limit, 0.5 = halve it
    reason: str = ""
    created_by: str = ""
    starts_at: datetime | None = None
    expires_at: datetime | None = None
    active: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiRateLimitOverride:
    def __init__(self) -> None:
        self._overrides: dict[tuple[str, str], RateLimitOverride] = {}

    def create(self, installation_id: str, override: RateLimitOverride) -> RateLimitOverride:
        if not installation_id:
            raise ValueError("installation_id is required")
        if override.multiplier <= 0:
            raise ValueError("multiplier must be positive")
        if override.multiplier > 10:
            raise ValueError("multiplier cannot exceed 10x")
        override.starts_at = override.starts_at or datetime.utcnow()
        if not override.expires_at:
            override.expires_at = override.starts_at + timedelta(hours=24)
        if override.expires_at <= override.starts_at:
            raise ValueError("expires_at must be after starts_at")
        key = (installation_id, override.override_id)
        self._overrides[key] = override
        log.info("rate_limit_override_created", installation_id=installation_id, consumer=override.consumer_id, multiplier=override.multiplier)
        return override

    def get_effective(self, installation_id: str, consumer_id: str, endpoint_path: str, now: datetime) -> float:
        best = 1.0
        for (inst, _), o in self._overrides.items():
            if inst != installation_id or o.consumer_id != consumer_id or not o.active:
                continue
            if o.starts_at and now < o.starts_at:
                continue
            if o.expires_at and now >= o.expires_at:
                continue
            if o.endpoint_path is not None and o.endpoint_path != endpoint_path:
                continue
            best = max(best, o.multiplier)
        return best

    def revoke(self, installation_id: str, override_id: str) -> RateLimitOverride:
        key = (installation_id, override_id)
        o = self._overrides.get(key)
        if not o:
            raise ValueError("Override not found")
        o.active = False
        return o

    def list_active(self, installation_id: str, consumer_id: str | None = None, now: datetime | None = None) -> list[RateLimitOverride]:
        now = now or datetime.utcnow()
        result = []
        for (inst, _), o in self._overrides.items():
            if inst != installation_id or not o.active:
                continue
            if consumer_id and o.consumer_id != consumer_id:
                continue
            if o.starts_at and now < o.starts_at:
                continue
            if o.expires_at and now >= o.expires_at:
                continue
            result.append(o)
        return result
