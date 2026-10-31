"""API Key Scope — manage fine-grained scopes for API keys."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class ApiKeyScope:
    key_id: str
    scopes: set[str] = field(default_factory=set)
    description: str = ""
    read_only: bool = False

VALID_SCOPES = {"read", "write", "delete", "admin", "webhooks:read", "webhooks:write", "analytics:read", "users:read", "users:write"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiKeyScope:
    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], ApiKeyScope] = {}

    def create_key(self, installation_id: str, key_id: str, scopes: list[str], description: str = "", read_only: bool = False) -> ApiKeyScope:
        if not installation_id: raise ValueError("installation_id is required")
        if not key_id: raise ValueError("key_id is required")
        if not scopes: raise ValueError("At least one scope required")
        invalid = set(scopes) - VALID_SCOPES
        if invalid: raise ValueError(f"Invalid scopes: {invalid}")
        if read_only:
            write_scopes = {s for s in scopes if "write" in s or s in ("delete", "admin")}
            if write_scopes: raise ValueError(f"Read-only key cannot have write scopes: {write_scopes}")
        key = (installation_id, key_id)
        if key in self._keys: raise ValueError(f"Key {key_id} already exists")
        ks = ApiKeyScope(key_id=key_id, scopes=set(scopes), description=description, read_only=read_only)
        self._keys[key] = ks
        return ks

    def check_scope(self, installation_id: str, key_id: str, required_scope: str) -> bool:
        ks = self._keys.get((installation_id, key_id))
        if ks is None: return False
        if "admin" in ks.scopes: return True
        return required_scope in ks.scopes

    def add_scope(self, installation_id: str, key_id: str, scope: str) -> ApiKeyScope:
        ks = self._get(installation_id, key_id)
        if scope not in VALID_SCOPES: raise ValueError(f"Invalid scope: {scope}")
        if ks.read_only and ("write" in scope or scope in ("delete", "admin")):
            raise ValueError("Cannot add write scope to read-only key")
        ks.scopes.add(scope)
        return ks

    def revoke_scope(self, installation_id: str, key_id: str, scope: str) -> ApiKeyScope:
        ks = self._get(installation_id, key_id)
        ks.scopes.discard(scope)
        return ks

    def list_keys(self, installation_id: str) -> list[ApiKeyScope]:
        return [ks for (inst, _), ks in self._keys.items() if inst == installation_id]

    def _get(self, installation_id: str, key_id: str) -> ApiKeyScope:
        ks = self._keys.get((installation_id, key_id))
        if ks is None: raise KeyError(f"Key {key_id} not found")
        return ks
