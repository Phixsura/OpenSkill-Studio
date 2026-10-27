"""App API Key Manager — lifecycle management for developer app API keys.

Manages API keys for installed developer apps:
- Key generation with configurable prefix and scopes
- Key rotation with overlap period
- Expiry and revocation
- Last-used tracking
- Per-installation key listing
- Scope validation on key use
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()

KEY_PREFIX = "osk_"
KEY_LENGTH = 32


class KeyStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"
    ROTATED = "rotated"


@dataclass
class ApiKey:
    """A managed API key."""

    key_id: str
    key_hash: str               # SHA-256 of raw key (raw never stored)
    key_prefix: str             # first 8 chars for display
    installation_id: str
    app_id: str
    scopes: list[str]
    status: KeyStatus = KeyStatus.ACTIVE
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    last_used_at: datetime | None = None
    revoked_at: datetime | None = None
    rotated_to: str | None = None  # key_id of replacement


@dataclass
class KeyValidation:
    """Result of validating an API key."""

    valid: bool
    key_id: str | None = None
    scopes: list[str] = field(default_factory=list)
    error: str | None = None


def _generate_raw_key() -> str:
    return KEY_PREFIX + secrets.token_urlsafe(KEY_LENGTH)


def _hash_key(raw: str) -> str:
    return hashlib.sha256(raw.encode()).hexdigest()


class AppApiKeyManager:
    """Manage API key lifecycle."""

    def __init__(self):
        # key_hash → ApiKey
        self._keys: dict[str, ApiKey] = {}
        self._next_id = 0

    def create(self, installation_id: str, app_id: str,
               scopes: list[str], ttl_days: int | None = None) -> tuple[str, ApiKey]:
        """Create a new API key. Returns (raw_key, key_record).

        The raw key is returned ONCE — it's never stored.
        """
        if not scopes:
            raise ValueError("At least one scope is required")

        raw = _generate_raw_key()
        key_hash = _hash_key(raw)

        self._next_id += 1
        key_id = f"key-{self._next_id}"
        expires = datetime.now(UTC) + timedelta(days=ttl_days) if ttl_days else None

        key = ApiKey(
            key_id=key_id, key_hash=key_hash,
            key_prefix=raw[:12] + "...",
            installation_id=installation_id, app_id=app_id,
            scopes=scopes, expires_at=expires,
        )
        self._keys[key_hash] = key
        log.info("api_key.created", key_id=key_id, installation_id=installation_id)
        return raw, key

    def validate(self, raw_key: str, required_scope: str | None = None,
                 now: datetime | None = None) -> KeyValidation:
        """Validate a raw API key. Updates last_used_at on success."""
        now = now or datetime.now(UTC)
        key_hash = _hash_key(raw_key)
        key = self._keys.get(key_hash)

        if key is None:
            return KeyValidation(valid=False, error="Invalid API key")

        if key.status == KeyStatus.REVOKED:
            return KeyValidation(valid=False, key_id=key.key_id, error="Key revoked")

        if key.status == KeyStatus.ROTATED:
            return KeyValidation(valid=False, key_id=key.key_id, error="Key rotated — use new key")

        if key.expires_at and now >= key.expires_at:
            key.status = KeyStatus.EXPIRED
            return KeyValidation(valid=False, key_id=key.key_id, error="Key expired")

        if required_scope and required_scope not in key.scopes:
            return KeyValidation(valid=False, key_id=key.key_id,
                                  scopes=key.scopes,
                                  error=f"Missing scope: {required_scope}")

        key.last_used_at = now
        return KeyValidation(valid=True, key_id=key.key_id, scopes=key.scopes)

    def rotate(self, raw_old_key: str, new_scopes: list[str] | None = None,
               overlap_hours: int = 24) -> tuple[str, ApiKey] | None:
        """Rotate a key: create new, mark old as rotated with overlap.

        Scope reduction only — cannot expand scopes on rotation.
        Overlap capped at 24h. Already-rotated keys cannot be rotated again.
        """
        old_hash = _hash_key(raw_old_key)
        old_key = self._keys.get(old_hash)
        if old_key is None or old_key.status != KeyStatus.ACTIVE:
            return None
        if old_key.rotated_to is not None:
            return None  # already rotated

        scopes = new_scopes or old_key.scopes
        # Scope expansion check: new scopes must be subset of old
        if not set(scopes) <= set(old_key.scopes):
            raise PermissionError("Cannot expand scopes on rotation")

        raw_new, new_key = self.create(old_key.installation_id, old_key.app_id, scopes)

        overlap_hours = min(overlap_hours, 24)  # cap overlap
        old_key.rotated_to = new_key.key_id
        old_key.expires_at = datetime.now(UTC) + timedelta(hours=overlap_hours)
        # Old key stays ACTIVE during overlap, validate() checks expires_at

        log.info("api_key.rotated", old_id=old_key.key_id, new_id=new_key.key_id)
        return raw_new, new_key

    def revoke(self, installation_id: str, key_id: str) -> bool:
        """Revoke a key by key_id. Requires installation_id ownership to prevent IDOR."""
        for key in self._keys.values():
            if key.key_id == key_id and key.installation_id == installation_id:
                key.status = KeyStatus.REVOKED
                key.revoked_at = datetime.now(UTC)
                return True
        return False

    def list_keys(self, installation_id: str) -> list[ApiKey]:
        """List all keys for an installation (never includes raw key)."""
        return sorted(
            [k for k in self._keys.values() if k.installation_id == installation_id],
            key=lambda k: k.created_at, reverse=True,
        )

    def get_active_count(self, installation_id: str) -> int:
        return sum(1 for k in self._keys.values()
                   if k.installation_id == installation_id and k.status == KeyStatus.ACTIVE)
