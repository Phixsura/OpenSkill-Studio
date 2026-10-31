"""API Consumer Rate Limit Override — temporary rate limit overrides per consumer."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitOverride:
    override_id: str
    consumer_id: str
    endpoint: str
    original_rpm: int
    override_rpm: int
    reason: str = ""
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    active: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiRateLimitOverride:
    def __init__(self) -> None:
        self._overrides: dict[tuple[str, str], RateLimitOverride] = {}

    def create_override(self, installation_id: str, override: RateLimitOverride) -> RateLimitOverride:
        if not installation_id: raise ValueError("installation_id is required")
        if override.override_rpm < 1: raise ValueError("override_rpm must be >= 1")
        if override.expires_at > 0 and override.expires_at <= time.time(): raise ValueError("expires_at must be in the future")
        key = (installation_id, override.override_id)
        if key in self._overrides: raise ValueError(f"Override {override.override_id} exists")
        self._overrides[key] = override
        return override

    def get_effective_rpm(self, installation_id: str, consumer_id: str, endpoint: str, default_rpm: int) -> int:
        now = time.time()
        for (inst, _), o in self._overrides.items():
            if inst == installation_id and o.consumer_id == consumer_id and o.endpoint == endpoint and o.active:
                if o.expires_at > 0 and o.expires_at < now:
                    o.active = False
                    continue
                return o.override_rpm
        return default_rpm

    def revoke(self, installation_id: str, override_id: str) -> RateLimitOverride:
        o = self._overrides.get((installation_id, override_id))
        if o is None: raise KeyError(f"Override {override_id} not found")
        o.active = False
        return o

    def active_overrides(self, installation_id: str) -> list[RateLimitOverride]:
        now = time.time()
        return [o for (inst, _), o in self._overrides.items() if inst == installation_id and o.active and (o.expires_at == 0 or o.expires_at > now)]

    def override_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._overrides if inst == installation_id)
