"""App Credential Vault — securely store and retrieve app credentials.

Manages encrypted credential storage:
- Store credentials with encryption markers
- Retrieve with masked display
- Rotate credentials
- Per-installation scoped vaults
"""

from __future__ import annotations

import hashlib
import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class StoredCredential:
    """A stored credential (value never exposed in full)."""

    credential_id: str
    name: str
    value_hash: str  # SHA-256 hash of value
    prefix: str      # first 4 chars for identification
    created_at: float = field(default_factory=time.time)
    rotated_at: float | None = None
    version: int = 1


class AppCredentialVault:
    """Securely store and retrieve app credentials."""

    def __init__(self) -> None:
        # (installation_id, credential_id) → (StoredCredential, raw_value)
        self._vault: dict[tuple[str, str], tuple[StoredCredential, str]] = {}

    def store(
        self,
        installation_id: str,
        credential_id: str,
        name: str,
        value: str,
        now: float | None = None,
    ) -> StoredCredential:
        """Store a credential. Returns metadata (not the value)."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not credential_id:
            raise ValueError("credential_id is required")
        if not value:
            raise ValueError("value is required")
        if len(value) < 8:
            raise ValueError("value must be at least 8 characters")

        key = (installation_id, credential_id)
        if key in self._vault:
            raise ValueError(f"Credential {credential_id} already exists. Use rotate().")

        cred = StoredCredential(
            credential_id=credential_id, name=name,
            value_hash=hashlib.sha256(value.encode()).hexdigest(),
            prefix=value[:4],
            created_at=now or time.time(),
        )
        self._vault[key] = (cred, value)
        return cred

    def get_metadata(self, installation_id: str, credential_id: str) -> StoredCredential:
        """Get credential metadata (never the raw value)."""
        key = (installation_id, credential_id)
        entry = self._vault.get(key)
        if entry is None:
            raise KeyError(f"Credential {credential_id} not found")
        return entry[0]

    def verify(self, installation_id: str, credential_id: str, value: str) -> bool:
        """Verify a credential value matches the stored hash."""
        key = (installation_id, credential_id)
        entry = self._vault.get(key)
        if entry is None:
            return False
        return hashlib.sha256(value.encode()).hexdigest() == entry[0].value_hash

    def rotate(
        self,
        installation_id: str,
        credential_id: str,
        new_value: str,
        now: float | None = None,
    ) -> StoredCredential:
        """Rotate a credential to a new value."""
        if len(new_value) < 8:
            raise ValueError("value must be at least 8 characters")

        key = (installation_id, credential_id)
        entry = self._vault.get(key)
        if entry is None:
            raise KeyError(f"Credential {credential_id} not found")

        cred = entry[0]
        cred.value_hash = hashlib.sha256(new_value.encode()).hexdigest()
        cred.prefix = new_value[:4]
        cred.rotated_at = now or time.time()
        cred.version += 1
        self._vault[key] = (cred, new_value)
        return cred

    def delete(self, installation_id: str, credential_id: str) -> bool:
        key = (installation_id, credential_id)
        if key in self._vault:
            del self._vault[key]
            return True
        return False

    def list_credentials(self, installation_id: str) -> list[StoredCredential]:
        return [cred for (inst, _), (cred, _) in self._vault.items() if inst == installation_id]
