"""App API Key Manager — manage API keys for installed apps.

Manages API key lifecycle:
- Create keys with scopes and expiry
- Revoke keys
- Validate keys with scope checking
- Key prefix for identification (first 8 chars visible)
- Per-installation scoped keys
- Last-used tracking
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

KEY_PREFIX_LEN = 8


@dataclass
class ApiKey:
    """An API key record."""

    key_id: str
    installation_id: str
    name: str
    prefix: str  # first 8 chars for display
    key_hash: str  # SHA-256 of full key
    scopes: list[str]
    created_at: float = field(default_factory=time.time)
    expires_at: float | None = None
    revoked: bool = False
    revoked_at: float | None = None
    last_used_at: float | None = None


@dataclass
class KeyValidation:
    """Result of validating an API key."""

    valid: bool
    key_id: str | None = None
    installation_id: str | None = None
    scopes: list[str] | None = None
    reason: str = ""


def _hash_key(raw_key: str) -> str:
    return hashlib.sha256(raw_key.encode()).hexdigest()


class AppApiKeyManager:
    """Manage API keys for installed apps."""

    def __init__(self) -> None:
        # (installation_id, key_id) → ApiKey
        self._keys: dict[tuple[str, str], ApiKey] = {}
        # key_hash → (installation_id, key_id) for lookup
        self._hash_index: dict[str, tuple[str, str]] = {}

    def create_key(
        self,
        installation_id: str,
        key_id: str,
        name: str,
        scopes: list[str] | None = None,
        expires_in_seconds: float | None = None,
    ) -> tuple[ApiKey, str]:
        """Create a new API key. Returns (record, raw_key)."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not key_id:
            raise ValueError("key_id is required")
        if not name:
            raise ValueError("name is required")

        compound = (installation_id, key_id)
        if compound in self._keys:
            raise ValueError(f"Key {key_id} already exists")

        raw_key = secrets.token_urlsafe(32)
        key_hash = _hash_key(raw_key)
        now = time.time()

        record = ApiKey(
            key_id=key_id,
            installation_id=installation_id,
            name=name,
            prefix=raw_key[:KEY_PREFIX_LEN],
            key_hash=key_hash,
            scopes=scopes or [],
            created_at=now,
            expires_at=now + expires_in_seconds if expires_in_seconds else None,
        )

        self._keys[compound] = record
        self._hash_index[key_hash] = compound
        log.info("api_key.created", key_id=key_id, name=name)
        return record, raw_key

    def validate_key(
        self,
        raw_key: str,
        required_scope: str | None = None,
        now: float | None = None,
    ) -> KeyValidation:
        """Validate a raw API key and optionally check scope."""
        now = now or time.time()
        key_hash = _hash_key(raw_key)
        compound = self._hash_index.get(key_hash)

        if compound is None:
            return KeyValidation(valid=False, reason="key_not_found")

        record = self._keys[compound]

        if record.revoked:
            return KeyValidation(valid=False, key_id=record.key_id, reason="revoked")

        if record.expires_at and now >= record.expires_at:
            return KeyValidation(valid=False, key_id=record.key_id, reason="expired")

        if required_scope and required_scope not in record.scopes:
            return KeyValidation(
                valid=False, key_id=record.key_id,
                installation_id=record.installation_id,
                scopes=record.scopes, reason="insufficient_scope",
            )

        # Track last used
        record.last_used_at = now

        return KeyValidation(
            valid=True,
            key_id=record.key_id,
            installation_id=record.installation_id,
            scopes=record.scopes,
        )

    def revoke_key(self, installation_id: str, key_id: str) -> ApiKey:
        """Revoke an API key."""
        record = self._get(installation_id, key_id)
        if record.revoked:
            raise ValueError("Key already revoked")
        record.revoked = True
        record.revoked_at = time.time()
        log.info("api_key.revoked", key_id=key_id)
        return record

    def get_key(self, installation_id: str, key_id: str) -> ApiKey:
        return self._get(installation_id, key_id)

    def list_keys(self, installation_id: str, include_revoked: bool = False) -> list[ApiKey]:
        """List keys for an installation."""
        keys = [
            record for (inst, _), record in self._keys.items()
            if inst == installation_id
        ]
        if not include_revoked:
            keys = [k for k in keys if not k.revoked]
        return keys

    def _get(self, installation_id: str, key_id: str) -> ApiKey:
        compound = (installation_id, key_id)
        record = self._keys.get(compound)
        if record is None:
            raise KeyError(f"Key {key_id} not found")
        return record
