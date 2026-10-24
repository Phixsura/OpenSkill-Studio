"""API key scope manager — manage scoped API keys with fine-grained permissions."""
from __future__ import annotations
import secrets, hashlib


class KeyScopeManager:
    def __init__(self):
        self._keys: dict[str, dict] = {}

    def create_key(self, name: str, scopes: list[str], owner: str) -> dict:
        key = f"osk_{secrets.token_urlsafe(24)}"
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        self._keys[key_hash] = {"name": name, "scopes": set(scopes), "owner": owner,
                                 "active": True, "usage_count": 0}
        return {"key": key, "name": name, "scopes": sorted(scopes)}

    def check_scope(self, key_hash: str, required_scope: str) -> dict:
        entry = self._keys.get(key_hash)
        if not entry or not entry["active"]:
            return {"allowed": False, "reason": "key_not_found_or_inactive"}
        allowed = required_scope in entry["scopes"] or "*" in entry["scopes"]
        if allowed:
            entry["usage_count"] += 1
        return {"allowed": allowed, "scope": required_scope, "name": entry["name"]}

    def revoke(self, key_hash: str) -> dict:
        if key_hash in self._keys:
            self._keys[key_hash]["active"] = False
            return {"revoked": True}
        return {"revoked": False}

    def list_keys(self) -> list[dict]:
        return [{"name": k["name"], "scopes": sorted(k["scopes"]),
                 "active": k["active"], "usage": k["usage_count"]}
                for k in self._keys.values()]
