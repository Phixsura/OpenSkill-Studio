"""API Consumer Credential Vault — secure storage for consumer credentials."""
from __future__ import annotations
from dataclasses import dataclass, field
import hashlib
import time
import structlog

log = structlog.get_logger()

@dataclass
class VaultEntry:
    entry_id: str
    credential_type: str  # "api_key", "oauth_token", "webhook_secret", "client_secret"
    masked_value: str  # only last 4 chars visible
    hash_value: str  # SHA-256 for verification
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0  # 0 = no expiry
    rotated: bool = False

VALID_TYPES = {"api_key", "oauth_token", "webhook_secret", "client_secret"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerCredentialVault:
    def __init__(self) -> None:
        self._vault: dict[tuple[str, str, str], VaultEntry] = {}

    def store(self, installation_id: str, consumer_id: str, entry_id: str, credential_type: str, value: str, expires_at: float = 0.0) -> VaultEntry:
        if not installation_id: raise ValueError("installation_id is required")
        if credential_type not in VALID_TYPES: raise ValueError(f"Invalid type: {credential_type}")
        if len(value) < 8: raise ValueError("Credential must be at least 8 characters")
        masked = "***" + value[-4:]
        hashed = hashlib.sha256(value.encode()).hexdigest()
        entry = VaultEntry(entry_id=entry_id, credential_type=credential_type, masked_value=masked, hash_value=hashed, expires_at=expires_at)
        self._vault[(installation_id, consumer_id, entry_id)] = entry
        return entry

    def verify(self, installation_id: str, consumer_id: str, entry_id: str, value: str) -> bool:
        entry = self._vault.get((installation_id, consumer_id, entry_id))
        if entry is None: return False
        if entry.expires_at > 0 and entry.expires_at < time.time(): return False
        if entry.rotated: return False
        return hashlib.sha256(value.encode()).hexdigest() == entry.hash_value

    def rotate(self, installation_id: str, consumer_id: str, entry_id: str, new_value: str) -> VaultEntry:
        key = (installation_id, consumer_id, entry_id)
        old = self._vault.get(key)
        if old is None: raise KeyError(f"Entry {entry_id} not found")
        old.rotated = True
        if len(new_value) < 8: raise ValueError("Credential must be at least 8 characters")
        new_entry = VaultEntry(entry_id=entry_id, credential_type=old.credential_type, masked_value="***" + new_value[-4:], hash_value=hashlib.sha256(new_value.encode()).hexdigest())
        self._vault[key] = new_entry
        return new_entry

    def list_entries(self, installation_id: str, consumer_id: str) -> list[VaultEntry]:
        return [e for (inst, cid, _), e in self._vault.items() if inst == installation_id and cid == consumer_id]

    def revoke(self, installation_id: str, consumer_id: str, entry_id: str) -> bool:
        key = (installation_id, consumer_id, entry_id)
        if key in self._vault: del self._vault[key]; return True
        return False

    def entry_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _, _) in self._vault if inst == installation_id)
