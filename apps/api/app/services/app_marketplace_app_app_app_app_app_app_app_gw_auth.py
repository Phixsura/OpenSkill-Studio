"""API gateway auth middleware — authenticate requests at the gateway level."""
from __future__ import annotations
import hashlib, secrets


class GatewayAuth:
    def __init__(self):
        self._api_keys: dict[str, dict] = {}
        self._auth_count = 0
        self._denied_count = 0

    def register_key(self, key: str, owner: str, scopes: list[str]) -> dict:
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        self._api_keys[key_hash] = {"owner": owner, "scopes": set(scopes), "active": True}
        return {"registered": True, "owner": owner}

    def authenticate(self, key: str, required_scope: str = "") -> dict:
        self._auth_count += 1
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        entry = self._api_keys.get(key_hash)
        if not entry or not entry["active"]:
            self._denied_count += 1
            return {"authenticated": False, "reason": "invalid_key"}
        if required_scope and required_scope not in entry["scopes"] and "*" not in entry["scopes"]:
            self._denied_count += 1
            return {"authenticated": False, "reason": "insufficient_scope"}
        return {"authenticated": True, "owner": entry["owner"]}

    def stats(self) -> dict:
        return {"total_auth": self._auth_count, "denied": self._denied_count,
                "keys_registered": len(self._api_keys)}
