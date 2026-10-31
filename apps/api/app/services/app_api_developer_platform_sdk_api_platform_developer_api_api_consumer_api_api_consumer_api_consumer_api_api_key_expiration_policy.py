"""Consumer API Key Expiration Policy — enforce key expiration policies."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class ExpirationPolicy:
    consumer_id: str
    max_lifetime_days: int = 365
    warn_before_days: int = 30
    auto_disable: bool = True
    require_rotation: bool = True

@dataclass
class KeyExpiration:
    key_id: str
    consumer_id: str
    created_at: datetime
    expires_at: datetime
    status: str = "active"  # "active", "warning", "expired", "disabled"

@dataclass
class ExpirationCheck:
    key_id: str
    status: str
    days_remaining: int
    action_required: bool

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiApiKeyExpirationPolicy:
    def __init__(self) -> None:
        self._policies: dict[tuple[str, str], ExpirationPolicy] = {}
        self._keys: dict[tuple[str, str, str], KeyExpiration] = {}

    def set_policy(self, installation_id: str, policy: ExpirationPolicy) -> ExpirationPolicy:
        if not installation_id:
            raise ValueError("installation_id is required")
        if policy.max_lifetime_days < 1:
            raise ValueError("max_lifetime_days must be positive")
        if policy.warn_before_days >= policy.max_lifetime_days:
            raise ValueError("warn_before_days must be less than max_lifetime_days")
        self._policies[(installation_id, policy.consumer_id)] = policy
        return policy

    def register_key(self, installation_id: str, consumer_id: str, key_id: str, created_at: datetime) -> KeyExpiration:
        policy = self._policies.get((installation_id, consumer_id), ExpirationPolicy(consumer_id=consumer_id))
        expires_at = created_at + timedelta(days=policy.max_lifetime_days)
        ke = KeyExpiration(key_id=key_id, consumer_id=consumer_id, created_at=created_at, expires_at=expires_at)
        self._keys[(installation_id, consumer_id, key_id)] = ke
        return ke

    def check(self, installation_id: str, consumer_id: str, key_id: str, now: datetime) -> ExpirationCheck:
        ke = self._keys.get((installation_id, consumer_id, key_id))
        if not ke:
            raise ValueError("Key not found")
        policy = self._policies.get((installation_id, consumer_id), ExpirationPolicy(consumer_id=consumer_id))
        days_remaining = (ke.expires_at - now).days
        if days_remaining <= 0:
            status = "expired"
            if policy.auto_disable:
                ke.status = "disabled"
        elif days_remaining <= policy.warn_before_days:
            status = "warning"
            ke.status = "warning"
        else:
            status = "active"
        return ExpirationCheck(key_id=key_id, status=status, days_remaining=max(0, days_remaining), action_required=status != "active")

    def list_expiring(self, installation_id: str, now: datetime) -> list[ExpirationCheck]:
        results = []
        for (inst, cid, kid), ke in self._keys.items():
            if inst != installation_id:
                continue
            check = self.check(installation_id, cid, kid, now)
            if check.action_required:
                results.append(check)
        return sorted(results, key=lambda c: c.days_remaining)
