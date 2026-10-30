"""API Consumer Rate Limit Exemption — grant temporary rate limit exemptions."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class RateLimitExemption:
    exemption_id: str
    consumer_id: str
    reason: str
    multiplier: float = 2.0  # multiply normal limits
    expires_at: float = 0.0
    created_at: float = field(default_factory=time.time)
    active: bool = True

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiRateLimitExemption:
    def __init__(self) -> None:
        self._exemptions: dict[tuple[str, str], RateLimitExemption] = {}

    def grant(self, installation_id: str, exemption: RateLimitExemption) -> RateLimitExemption:
        if not installation_id: raise ValueError("installation_id is required")
        if exemption.multiplier < 1.0: raise ValueError("multiplier must be >= 1.0")
        if exemption.expires_at > 0 and exemption.expires_at <= time.time(): raise ValueError("expires_at must be in the future")
        self._exemptions[(installation_id, exemption.consumer_id)] = exemption
        return exemption

    def get_multiplier(self, installation_id: str, consumer_id: str) -> float:
        ex = self._exemptions.get((installation_id, consumer_id))
        if ex is None or not ex.active: return 1.0
        if ex.expires_at > 0 and ex.expires_at < time.time():
            ex.active = False
            return 1.0
        return ex.multiplier

    def revoke(self, installation_id: str, consumer_id: str) -> bool:
        ex = self._exemptions.get((installation_id, consumer_id))
        if ex and ex.active: ex.active = False; return True
        return False

    def active_exemptions(self, installation_id: str) -> list[RateLimitExemption]:
        now = time.time()
        result = []
        for (inst, _), ex in self._exemptions.items():
            if inst == installation_id and ex.active:
                if ex.expires_at > 0 and ex.expires_at < now: ex.active = False
                else: result.append(ex)
        return result

    def list_exemptions(self, installation_id: str) -> list[RateLimitExemption]:
        return [e for (inst, _), e in self._exemptions.items() if inst == installation_id]
