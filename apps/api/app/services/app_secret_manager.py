"""App Secret Manager — secure key-value secret storage for installed apps.

Provides encrypted-at-rest secret management for the developer platform:
- Per-installation scoped secrets (no cross-app access)
- Key rotation with grace period (old value readable during overlap)
- Version tracking per secret
- Access audit trail
- Masked listing (values never returned in list operations)
- TTL-based auto-expiry
- Size and count limits per installation
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import Enum

import structlog

log = structlog.get_logger()

MAX_SECRETS_PER_INSTALL = 50
MAX_SECRET_KEY_LENGTH = 128
MAX_SECRET_VALUE_LENGTH = 8192  # 8KB


class SecretAccessType(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ROTATE = "rotate"


@dataclass
class SecretEntry:
    """A stored secret with versioning."""

    key: str
    value: str                     # in production: encrypted at rest
    version: int
    installation_id: str
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None
    previous_value: str | None = None     # during rotation grace period
    previous_expires_at: datetime | None = None


@dataclass
class SecretMetadata:
    """Metadata returned in listings (never includes value)."""

    key: str
    version: int
    created_at: datetime
    updated_at: datetime
    expires_at: datetime | None = None
    has_previous: bool = False
    value_hash: str = ""           # SHA-256 prefix for verification


@dataclass
class AccessLogEntry:
    """Audit entry for secret access."""

    installation_id: str
    key: str
    access_type: SecretAccessType
    actor_id: str
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class SecretResult:
    """Result of a secret operation."""

    success: bool
    key: str | None = None
    value: str | None = None
    version: int | None = None
    error: str | None = None


class AppSecretManager:
    """Per-installation secret store with rotation and audit."""

    def __init__(self):
        # (installation_id, key) → SecretEntry
        self._secrets: dict[tuple[str, str], SecretEntry] = {}
        self._access_log: list[AccessLogEntry] = []

    # ── Write ────────────────────────────────────────────

    def set_secret(self, installation_id: str, key: str, value: str,
                   actor_id: str, ttl_seconds: int | None = None) -> SecretResult:
        """Set or update a secret. Returns the new version."""
        if not key or len(key) > MAX_SECRET_KEY_LENGTH:
            return SecretResult(success=False, error=f"Key must be 1-{MAX_SECRET_KEY_LENGTH} chars")
        if len(value) > MAX_SECRET_VALUE_LENGTH:
            return SecretResult(success=False, error=f"Value exceeds {MAX_SECRET_VALUE_LENGTH} bytes")

        # Count check
        existing_count = sum(
            1 for (iid, _) in self._secrets if iid == installation_id
        )
        compound = (installation_id, key)
        if compound not in self._secrets and existing_count >= MAX_SECRETS_PER_INSTALL:
            return SecretResult(success=False,
                                error=f"Limit reached: {MAX_SECRETS_PER_INSTALL} secrets per installation")

        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=ttl_seconds) if ttl_seconds else None

        existing = self._secrets.get(compound)
        if existing:
            version = existing.version + 1
            entry = SecretEntry(
                key=key, value=value, version=version,
                installation_id=installation_id,
                created_at=existing.created_at, updated_at=now,
                expires_at=expires_at,
            )
        else:
            entry = SecretEntry(
                key=key, value=value, version=1,
                installation_id=installation_id,
                created_at=now, updated_at=now,
                expires_at=expires_at,
            )

        self._secrets[compound] = entry
        self._log_access(installation_id, key, SecretAccessType.WRITE, actor_id)
        return SecretResult(success=True, key=key, version=entry.version)

    def rotate_secret(self, installation_id: str, key: str,
                      new_value: str, actor_id: str,
                      grace_seconds: int = 300) -> SecretResult:
        """Rotate a secret: set new value, keep old readable during grace period."""
        compound = (installation_id, key)
        existing = self._secrets.get(compound)
        if existing is None:
            return SecretResult(success=False, error="Secret not found")

        if len(new_value) > MAX_SECRET_VALUE_LENGTH:
            return SecretResult(success=False, error=f"Value exceeds {MAX_SECRET_VALUE_LENGTH} bytes")

        now = datetime.now(UTC)
        existing.previous_value = existing.value
        existing.previous_expires_at = now + timedelta(seconds=grace_seconds)
        existing.value = new_value
        existing.version += 1
        existing.updated_at = now

        self._log_access(installation_id, key, SecretAccessType.ROTATE, actor_id)
        log.info("secret.rotated", installation_id=installation_id, key=key,
                 version=existing.version, grace_seconds=grace_seconds)
        return SecretResult(success=True, key=key, version=existing.version)

    # ── Read ─────────────────────────────────────────────

    def get_secret(self, installation_id: str, key: str,
                   actor_id: str) -> SecretResult:
        """Read a secret value. Checks expiry."""
        compound = (installation_id, key)
        entry = self._secrets.get(compound)
        if entry is None:
            return SecretResult(success=False, error="Secret not found")

        now = datetime.now(UTC)
        if entry.expires_at and entry.expires_at <= now:
            # Expired — clean up
            del self._secrets[compound]
            return SecretResult(success=False, error="Secret has expired")

        self._log_access(installation_id, key, SecretAccessType.READ, actor_id)
        return SecretResult(success=True, key=key, value=entry.value, version=entry.version)

    def get_previous_value(self, installation_id: str, key: str,
                           actor_id: str) -> SecretResult:
        """Read the previous value during rotation grace period."""
        compound = (installation_id, key)
        entry = self._secrets.get(compound)
        if entry is None:
            return SecretResult(success=False, error="Secret not found")

        now = datetime.now(UTC)
        if (entry.previous_value is None
            or entry.previous_expires_at is None
            or entry.previous_expires_at <= now):
            return SecretResult(success=False, error="No previous value or grace period expired")

        self._log_access(installation_id, key, SecretAccessType.READ, actor_id)
        return SecretResult(success=True, key=key, value=entry.previous_value,
                            version=entry.version - 1)

    # ── Delete ───────────────────────────────────────────

    def delete_secret(self, installation_id: str, key: str,
                      actor_id: str) -> SecretResult:
        compound = (installation_id, key)
        if compound not in self._secrets:
            return SecretResult(success=False, error="Secret not found")
        del self._secrets[compound]
        self._log_access(installation_id, key, SecretAccessType.DELETE, actor_id)
        return SecretResult(success=True, key=key)

    def delete_all(self, installation_id: str, actor_id: str) -> int:
        """Delete all secrets for an installation (e.g. on uninstall)."""
        keys = [k for (iid, k) in self._secrets if iid == installation_id]
        for key in keys:
            del self._secrets[(installation_id, key)]
            self._log_access(installation_id, key, SecretAccessType.DELETE, actor_id)
        return len(keys)

    # ── Listing ──────────────────────────────────────────

    def list_secrets(self, installation_id: str) -> list[SecretMetadata]:
        """List secret metadata (never returns values)."""
        result = []
        now = datetime.now(UTC)
        for (iid, key), entry in sorted(self._secrets.items()):
            if iid != installation_id:
                continue
            if entry.expires_at and entry.expires_at <= now:
                continue
            has_prev = (entry.previous_value is not None
                        and entry.previous_expires_at is not None
                        and entry.previous_expires_at > now)
            result.append(SecretMetadata(
                key=entry.key,
                version=entry.version,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
                expires_at=entry.expires_at,
                has_previous=has_prev,
                value_hash=hashlib.sha256(entry.value.encode()).hexdigest()[:16],
            ))
        return result

    def count(self, installation_id: str) -> int:
        return sum(1 for (iid, _) in self._secrets if iid == installation_id)

    # ── Audit ────────────────────────────────────────────

    def get_access_log(self, installation_id: str,
                       limit: int = 50) -> list[AccessLogEntry]:
        """Get access log scoped to an installation. Always filters."""
        entries = [e for e in self._access_log if e.installation_id == installation_id]
        return entries[-limit:]

    def _log_access(self, installation_id: str, key: str,
                    access_type: SecretAccessType, actor_id: str) -> None:
        self._access_log.append(AccessLogEntry(
            installation_id=installation_id,
            key=key,
            access_type=access_type,
            actor_id=actor_id,
        ))
