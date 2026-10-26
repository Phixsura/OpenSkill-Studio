"""Sandbox API Key Scope — fine-grained API key permissions with scoping.

Manages API keys with per-endpoint scopes, IP restrictions,
expiration, usage limits, and scope inheritance.
"""
from __future__ import annotations
import hashlib
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class ScopedApiKey:
    key_id: str
    key_hash: str
    sandbox_id: str
    name: str
    scopes: set[str]
    ip_allowlist: list[str] = field(default_factory=list)
    rate_limit: int = 0  # 0 = unlimited
    expires_at: float = 0  # 0 = no expiry
    usage_count: int = 0
    max_usage: int = 0  # 0 = unlimited
    revoked: bool = False
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


VALID_SCOPES = {
    "read:data", "write:data", "read:config", "write:config",
    "execute:function", "manage:webhooks", "manage:secrets",
    "admin:sandbox", "read:metrics", "read:logs",
}


class SandboxApiKeyScopeService:
    """Manages scoped API keys for sandbox access control."""

    def __init__(self):
        self._keys: dict[str, ScopedApiKey] = {}
        self._hash_index: dict[str, str] = {}

    def _hash(self, raw: str) -> str:
        return hashlib.sha256(raw.encode()).hexdigest()

    def create_key(self, sandbox_id: str, name: str, scopes: list[str],
                   ip_allowlist: list[str] | None = None,
                   rate_limit: int = 0, expires_in: float = 0,
                   max_usage: int = 0) -> dict:
        for scope in scopes:
            if scope not in VALID_SCOPES:
                raise ValueError(f"Invalid scope: {scope}")

        raw_key = f"sbk_{secrets.token_urlsafe(32)}"
        key_id = f"kid_{secrets.token_urlsafe(8)}"
        key_hash = self._hash(raw_key)

        key = ScopedApiKey(
            key_id=key_id, key_hash=key_hash, sandbox_id=sandbox_id,
            name=name, scopes=set(scopes),
            ip_allowlist=ip_allowlist or [],
            rate_limit=rate_limit,
            expires_at=time.time() + expires_in if expires_in != 0 else 0,
            max_usage=max_usage,
        )
        self._keys[key_id] = key
        self._hash_index[key_hash] = key_id
        return {"key_id": key_id, "api_key": raw_key, "scopes": sorted(scopes)}

    def validate(self, raw_key: str, required_scope: str,
                 client_ip: str = "") -> dict:
        key_hash = self._hash(raw_key)
        key_id = self._hash_index.get(key_hash)
        if not key_id:
            return {"valid": False, "reason": "Key not found"}

        key = self._keys[key_id]
        if key.revoked:
            return {"valid": False, "reason": "Key revoked"}
        if key.expires_at and time.time() > key.expires_at:
            return {"valid": False, "reason": "Key expired"}
        if key.max_usage and key.usage_count >= key.max_usage:
            return {"valid": False, "reason": "Usage limit exceeded"}
        if key.ip_allowlist and (not client_ip or client_ip not in key.ip_allowlist):
            return {"valid": False, "reason": "IP not allowed"}
        if required_scope not in key.scopes:
            return {"valid": False, "reason": f"Missing scope: {required_scope}"}

        key.usage_count += 1
        return {"valid": True, "key_id": key_id, "sandbox_id": key.sandbox_id}

    def revoke(self, key_id: str) -> bool:
        key = self._keys.get(key_id)
        if key and not key.revoked:
            key.revoked = True
            return True
        return False

    def list_keys(self, sandbox_id: str) -> list[dict]:
        return [{"key_id": k.key_id, "name": k.name, "scopes": sorted(k.scopes),
                 "usage_count": k.usage_count, "revoked": k.revoked}
                for k in self._keys.values() if k.sandbox_id == sandbox_id]
