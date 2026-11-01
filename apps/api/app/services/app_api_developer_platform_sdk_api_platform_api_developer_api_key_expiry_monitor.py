"""App API Developer API Key Expiry Monitor — track API key expiration dates."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class KeyExpiry:
    key_id: str
    consumer_id: str
    expires_at: float
    days_until_expiry: float = 0.0

    @property
    def expired(self) -> bool:
        return time.time() > self.expires_at

    @property
    def expiring_soon(self) -> bool:
        return not self.expired and self.days_until_expiry <= 30

    @property
    def urgency(self) -> str:
        if self.expired: return "expired"
        if self.days_until_expiry <= 7: return "critical"
        if self.days_until_expiry <= 30: return "warning"
        return "ok"

class AppAPIDeveloperPlatformSDKApiPlatformApiDeveloperApiKeyExpiryMonitor:
    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], KeyExpiry] = {}

    def track(self, installation_id: str, key_id: str, consumer_id: str, expires_at: float) -> KeyExpiry:
        if not installation_id: raise ValueError("installation_id is required")
        days = max(0, (expires_at - time.time()) / 86400)
        k = KeyExpiry(key_id=key_id, consumer_id=consumer_id, expires_at=expires_at, days_until_expiry=round(days, 1))
        self._keys[(installation_id, key_id)] = k
        return k

    def expiring_soon(self, installation_id: str, days: int = 30) -> list[KeyExpiry]:
        return [k for (inst, _), k in self._keys.items() if inst == installation_id and not k.expired and k.days_until_expiry <= days]

    def expired_keys(self, installation_id: str) -> list[KeyExpiry]:
        return [k for (inst, _), k in self._keys.items() if inst == installation_id and k.expired]

    def all_keys(self, installation_id: str) -> list[KeyExpiry]:
        return sorted([k for (inst, _), k in self._keys.items() if inst == installation_id], key=lambda k: k.days_until_expiry)
