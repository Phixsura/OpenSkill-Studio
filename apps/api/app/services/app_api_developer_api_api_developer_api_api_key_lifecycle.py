"""App API Developer API Key Lifecycle — manage full API key lifecycle."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class APIKeyRecord:
    key_id: str
    name: str
    prefix: str
    key_hash: str
    status: str = "active"  # "active", "suspended", "revoked", "expired"
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    last_used_at: float | None = None
    usage_count: int = 0

    @property
    def expired(self) -> bool:
        return self.expires_at is not None and time.time() > self.expires_at

class AppAPIDeveloperAPIApiDeveloperApiApiKeyLifecycle:
    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], APIKeyRecord] = {}

    def create_key(self, installation_id: str, key_id: str, name: str, raw_key: str, expires_in_days: int | None = None) -> APIKeyRecord:
        if not installation_id: raise ValueError("installation_id is required")
        if len(raw_key) < 20: raise ValueError("key must be at least 20 chars")
        key = (installation_id, key_id)
        if key in self._keys: raise ValueError(f"Key {key_id} exists")
        prefix = raw_key[:8]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        expires_at = (time.time() + expires_in_days * 86400) if expires_in_days else None
        r = APIKeyRecord(key_id=key_id, name=name, prefix=prefix, key_hash=key_hash, expires_at=expires_at)
        self._keys[key] = r
        return r

    def use_key(self, installation_id: str, key_id: str) -> APIKeyRecord:
        r = self._get(installation_id, key_id)
        if r.status != "active": raise ValueError(f"Key is {r.status}")
        if r.expired:
            r.status = "expired"
            raise ValueError("Key has expired")
        r.last_used_at = time.time()
        r.usage_count += 1
        return r

    def suspend(self, installation_id: str, key_id: str) -> APIKeyRecord:
        r = self._get(installation_id, key_id)
        r.status = "suspended"
        return r

    def revoke(self, installation_id: str, key_id: str) -> APIKeyRecord:
        r = self._get(installation_id, key_id)
        r.status = "revoked"
        return r

    def reactivate(self, installation_id: str, key_id: str) -> APIKeyRecord:
        r = self._get(installation_id, key_id)
        if r.status == "revoked": raise ValueError("Cannot reactivate revoked key")
        r.status = "active"
        return r

    def active_keys(self, installation_id: str) -> list[APIKeyRecord]:
        return [r for (inst, _), r in self._keys.items() if inst == installation_id and r.status == "active" and not r.expired]

    def _get(self, installation_id: str, key_id: str) -> APIKeyRecord:
        key = (installation_id, key_id)
        r = self._keys.get(key)
        if r is None: raise KeyError(f"Key {key_id} not found")
        return r
