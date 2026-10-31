"""App API Key Rotation — scheduled key rotation with grace periods.

Manages API key lifecycle:
- Generate new keys with expiration
- Rotate keys with overlap grace period
- Revoke compromised keys immediately
- Per-installation scoped keys
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class APIKey:
    """An API key with lifecycle metadata."""

    key_id: str
    prefix: str  # first 8 chars for identification
    key_hash: str  # SHA-256 hash of full key
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked: bool = False
    label: str = ""

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return time.time() > self.expires_at

    @property
    def is_active(self) -> bool:
        return not self.revoked and not self.is_expired


class AppAPIKeyRotation:
    """Manage API key rotation with grace periods."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], APIKey] = {}

    def generate_key(
        self, installation_id: str, key_id: str, label: str = "",
        ttl_seconds: int | None = None,
    ) -> tuple[APIKey, str]:
        """Generate a new API key. Returns (metadata, raw_key)."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key_id:
            raise ValueError("key_id is required")

        raw_key = secrets.token_urlsafe(32)
        prefix = raw_key[:8]
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        expires_at = None
        if ttl_seconds is not None:
            if ttl_seconds <= 0:
                raise ValueError("ttl_seconds must be positive")
            expires_at = time.time() + ttl_seconds

        api_key = APIKey(
            key_id=key_id, prefix=prefix, key_hash=key_hash,
            expires_at=expires_at, label=label,
        )
        self._keys[(installation_id, key_id)] = api_key
        return api_key, raw_key

    def verify(self, installation_id: str, raw_key: str) -> APIKey | None:
        """Verify a raw key against stored hashes. Returns key if valid."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        for (inst, _), k in self._keys.items():
            if inst == installation_id and k.key_hash == key_hash and k.is_active:
                return k
        return None

    def rotate(
        self, installation_id: str, old_key_id: str, new_key_id: str,
        grace_seconds: int = 3600, new_ttl: int | None = None,
    ) -> tuple[APIKey, str]:
        """Rotate: generate new key and set old key to expire after grace period."""
        old = self._get(installation_id, old_key_id)
        if not old.is_active:
            raise ValueError("Old key is not active")

        # Set grace period on old key
        old.expires_at = time.time() + grace_seconds

        # Generate new key
        return self.generate_key(installation_id, new_key_id, label=old.label, ttl_seconds=new_ttl)

    def revoke(self, installation_id: str, key_id: str) -> APIKey:
        k = self._get(installation_id, key_id)
        k.revoked = True
        return k

    def list_keys(self, installation_id: str, active_only: bool = False) -> list[APIKey]:
        keys = [k for (inst, _), k in self._keys.items() if inst == installation_id]
        if active_only:
            keys = [k for k in keys if k.is_active]
        return keys

    def _get(self, installation_id: str, key_id: str) -> APIKey:
        key = (installation_id, key_id)
        k = self._keys.get(key)
        if k is None:
            raise KeyError(f"Key {key_id} not found")
        return k
