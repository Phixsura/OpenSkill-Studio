"""API Key Rotation — automated key rotation with grace period transitions.

Manages API key lifecycle with scheduled rotation, grace periods for
old keys, rotation history, and emergency revocation.
"""
from __future__ import annotations
import hashlib
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class ApiKey:
    key_id: str
    key_hash: str
    extension_id: str
    status: str = "active"  # active, grace, revoked
    created_at: float = 0.0
    expires_at: float = 0.0
    revoked_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


@dataclass
class RotationEvent:
    old_key_id: str
    new_key_id: str
    reason: str
    timestamp: float = 0.0


class KeyRotationService:
    """Manages API key rotation with grace periods."""

    DEFAULT_TTL = 86400 * 90  # 90 days
    GRACE_PERIOD = 86400 * 7  # 7 days

    def __init__(self):
        self._keys: dict[str, ApiKey] = {}
        self._by_extension: dict[str, list[str]] = {}
        self._hash_index: dict[str, str] = {}
        self._history: list[RotationEvent] = []

    def _hash(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    def generate(self, extension_id: str, ttl: float | None = None) -> dict:
        raw_key = f"sk_{secrets.token_urlsafe(32)}"
        key_id = f"kid_{secrets.token_urlsafe(8)}"
        key_hash = self._hash(raw_key)

        key = ApiKey(
            key_id=key_id, key_hash=key_hash,
            extension_id=extension_id,
            expires_at=time.time() + (ttl or self.DEFAULT_TTL),
        )
        self._keys[key_id] = key
        self._by_extension.setdefault(extension_id, []).append(key_id)
        self._hash_index[key_hash] = key_id

        return {"key_id": key_id, "api_key": raw_key, "expires_at": key.expires_at}

    def validate(self, raw_key: str) -> dict:
        key_hash = self._hash(raw_key)
        key_id = self._hash_index.get(key_hash)
        if not key_id:
            return {"valid": False, "reason": "Key not found"}
        key = self._keys[key_id]
        if key.status == "revoked":
            return {"valid": False, "reason": "Key revoked"}
        if time.time() > key.expires_at and key.status != "grace":
            return {"valid": False, "reason": "Key expired"}
        return {"valid": True, "key_id": key_id, "extension_id": key.extension_id,
                "status": key.status}

    def rotate(self, extension_id: str, reason: str = "scheduled") -> dict:
        old_keys = [self._keys[kid] for kid in self._by_extension.get(extension_id, [])
                    if self._keys[kid].status == "active"]

        # Generate new key
        new = self.generate(extension_id)

        # Move old keys to grace period
        for old_key in old_keys:
            old_key.status = "grace"
            old_key.expires_at = time.time() + self.GRACE_PERIOD
            self._history.append(RotationEvent(
                old_key_id=old_key.key_id, new_key_id=new["key_id"],
                reason=reason, timestamp=time.time(),
            ))

        return {
            "new_key": new, "grace_keys": len(old_keys),
            "grace_period_seconds": self.GRACE_PERIOD,
        }

    def revoke(self, key_id: str) -> bool:
        key = self._keys.get(key_id)
        if not key or key.status == "revoked":
            return False
        key.status = "revoked"
        key.revoked_at = time.time()
        return True

    def revoke_all(self, extension_id: str) -> int:
        count = 0
        for kid in self._by_extension.get(extension_id, []):
            key = self._keys[kid]
            if key.status != "revoked":
                key.status = "revoked"
                key.revoked_at = time.time()
                count += 1
        return count

    def get_active_keys(self, extension_id: str) -> list[dict]:
        return [
            {"key_id": self._keys[kid].key_id, "status": self._keys[kid].status,
             "created_at": self._keys[kid].created_at}
            for kid in self._by_extension.get(extension_id, [])
            if self._keys[kid].status in ("active", "grace")
        ]

    def get_rotation_history(self, extension_id: str) -> list[RotationEvent]:
        key_ids = set(self._by_extension.get(extension_id, []))
        return [e for e in self._history if e.new_key_id in key_ids or e.old_key_id in key_ids]
