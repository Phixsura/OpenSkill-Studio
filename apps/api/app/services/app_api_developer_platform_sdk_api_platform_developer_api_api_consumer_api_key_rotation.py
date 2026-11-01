"""API Consumer API Key Rotation — automated key rotation with grace periods."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class ApiKeyVersion:
    version: int
    key_hash: str
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    revoked: bool = False

@dataclass
class KeyRotation:
    consumer_id: str
    current_version: int = 0
    versions: list[ApiKeyVersion] = field(default_factory=list)
    grace_period_s: int = 3600  # both old and new keys work during grace

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiKeyRotation:
    def __init__(self) -> None:
        self._rotations: dict[tuple[str, str], KeyRotation] = {}

    def issue_key(self, installation_id: str, consumer_id: str, grace_period_s: int = 3600) -> dict[str, str]:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, consumer_id)
        raw = secrets.token_urlsafe(32)
        key_hash = hashlib.sha256(raw.encode()).hexdigest()
        rot = self._rotations.get(key)
        if rot is None:
            rot = KeyRotation(consumer_id=consumer_id, grace_period_s=grace_period_s)
            self._rotations[key] = rot
        rot.current_version += 1
        ver = ApiKeyVersion(version=rot.current_version, key_hash=key_hash)
        rot.versions.append(ver)
        # Expire old versions after grace period
        now = time.time()
        for v in rot.versions[:-1]:
            if not v.revoked and v.expires_at == 0:
                v.expires_at = now + rot.grace_period_s
        return {"key": raw, "version": rot.current_version}

    def validate(self, installation_id: str, consumer_id: str, raw_key: str) -> dict[str, object]:
        rot = self._rotations.get((installation_id, consumer_id))
        if rot is None: return {"valid": False, "reason": "no_key"}
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        now = time.time()
        for v in reversed(rot.versions):
            if v.revoked: continue
            if v.expires_at > 0 and v.expires_at < now: continue
            if v.key_hash == key_hash:
                return {"valid": True, "version": v.version, "is_current": v.version == rot.current_version}
        return {"valid": False, "reason": "invalid_key"}

    def revoke_all(self, installation_id: str, consumer_id: str) -> int:
        rot = self._rotations.get((installation_id, consumer_id))
        if rot is None: return 0
        count = sum(1 for v in rot.versions if not v.revoked)
        for v in rot.versions: v.revoked = True
        return count

    def get_rotation(self, installation_id: str, consumer_id: str) -> KeyRotation | None:
        return self._rotations.get((installation_id, consumer_id))
