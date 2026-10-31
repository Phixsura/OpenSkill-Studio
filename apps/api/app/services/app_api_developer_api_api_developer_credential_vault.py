"""App API Developer Credential Vault — secure storage for developer credentials."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class VaultEntry:
    entry_id: str
    credential_type: str  # "api_key", "oauth_token", "jwt_secret", "webhook_secret"
    name: str
    fingerprint: str  # hash of actual value
    created_at: float = field(default_factory=time.time)
    last_accessed_at: float | None = None
    access_count: int = 0
    rotated: bool = False

class AppAPIDeveloperAPIApiDeveloperCredentialVault:
    def __init__(self) -> None:
        self._vault: dict[tuple[str, str], VaultEntry] = {}

    def store(self, installation_id: str, entry_id: str, credential_type: str, name: str, value: str) -> VaultEntry:
        if not installation_id: raise ValueError("installation_id is required")
        valid_types = {"api_key", "oauth_token", "jwt_secret", "webhook_secret"}
        if credential_type not in valid_types: raise ValueError(f"Invalid type: {credential_type}")
        if len(value) < 8: raise ValueError("Credential too short")
        fingerprint = hashlib.sha256(value.encode()).hexdigest()[:16]
        key = (installation_id, entry_id)
        e = VaultEntry(entry_id=entry_id, credential_type=credential_type, name=name, fingerprint=fingerprint)
        self._vault[key] = e
        return e

    def access(self, installation_id: str, entry_id: str) -> VaultEntry:
        key = (installation_id, entry_id)
        e = self._vault.get(key)
        if e is None: raise KeyError(f"Entry {entry_id} not found")
        e.last_accessed_at = time.time()
        e.access_count += 1
        return e

    def rotate(self, installation_id: str, entry_id: str, new_value: str) -> VaultEntry:
        key = (installation_id, entry_id)
        e = self._vault.get(key)
        if e is None: raise KeyError(f"Entry {entry_id} not found")
        if len(new_value) < 8: raise ValueError("Credential too short")
        e.fingerprint = hashlib.sha256(new_value.encode()).hexdigest()[:16]
        e.rotated = True
        return e

    def list_entries(self, installation_id: str) -> list[VaultEntry]:
        return [e for (inst, _), e in self._vault.items() if inst == installation_id]

    def by_type(self, installation_id: str, credential_type: str) -> list[VaultEntry]:
        return [e for e in self.list_entries(installation_id) if e.credential_type == credential_type]
