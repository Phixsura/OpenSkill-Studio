"""App API Key Scope — associate scopes with API keys.

Manages scoped API keys:
- Create keys with specific scope sets
- Validate key has required scope
- List keys by scope
- Per-installation scoped keys
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class ScopedAPIKey:
    """An API key with assigned scopes."""

    key_id: str
    prefix: str
    key_hash: str
    scopes: set[str]
    label: str = ""
    active: bool = True
    request_count: int = 0


class AppAPIKeyScope:
    """Associate scopes with API keys."""

    def __init__(self) -> None:
        self._keys: dict[tuple[str, str], ScopedAPIKey] = {}

    def create_key(
        self, installation_id: str, key_id: str, scopes: list[str],
        label: str = "",
    ) -> tuple[ScopedAPIKey, str]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not scopes:
            raise ValueError("at least one scope required")

        raw = secrets.token_urlsafe(32)
        key = ScopedAPIKey(
            key_id=key_id, prefix=raw[:8],
            key_hash=hashlib.sha256(raw.encode()).hexdigest(),
            scopes=set(scopes), label=label,
        )
        self._keys[(installation_id, key_id)] = key
        return key, raw

    def validate(self, installation_id: str, raw_key: str, required_scope: str) -> bool:
        """Check if key is valid and has required scope."""
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        for (inst, _), k in self._keys.items():
            if inst == installation_id and k.key_hash == key_hash and k.active:
                if required_scope in k.scopes:
                    k.request_count += 1
                    return True
                return False
        return False

    def revoke(self, installation_id: str, key_id: str) -> ScopedAPIKey:
        key = (installation_id, key_id)
        k = self._keys.get(key)
        if k is None:
            raise KeyError(f"Key {key_id} not found")
        k.active = False
        return k

    def list_keys(self, installation_id: str, scope: str | None = None) -> list[ScopedAPIKey]:
        keys = [k for (inst, _), k in self._keys.items() if inst == installation_id]
        if scope:
            keys = [k for k in keys if scope in k.scopes]
        return keys
