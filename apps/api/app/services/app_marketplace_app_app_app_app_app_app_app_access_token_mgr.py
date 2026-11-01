"""Access token manager — create, rotate, and revoke API tokens."""
from __future__ import annotations
import secrets
import hmac
import hashlib
import time

_HMAC_KEY = secrets.token_bytes(32)


class AccessTokenManager:
    def __init__(self):
        self._tokens: dict[str, dict] = {}

    def create_token(self, *, name: str, scopes: list[str],
                      expires_in: int = 86400) -> dict:
        raw = secrets.token_urlsafe(32)
        token_hash = hmac.new(_HMAC_KEY, raw.encode(), hashlib.sha256).hexdigest()
        prefix = raw[:8]
        created = time.time()
        self._tokens[token_hash] = {
            "name": name, "prefix": prefix, "scopes": scopes,
            "created": created, "expires": created + expires_in,
            "revoked": False, "last_used": None,
        }
        return {"token": raw, "prefix": prefix, "name": name,
                "scopes": scopes, "expires_in": expires_in}

    def validate_token(self, raw: str, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        token_hash = hmac.new(_HMAC_KEY, raw.encode(), hashlib.sha256).hexdigest()
        entry = self._tokens.get(token_hash)
        if not entry:
            return {"valid": False, "reason": "not_found"}
        if entry["revoked"]:
            return {"valid": False, "reason": "revoked"}
        if ts > entry["expires"]:
            return {"valid": False, "reason": "expired"}
        entry["last_used"] = ts
        return {"valid": True, "name": entry["name"], "scopes": entry["scopes"]}

    def revoke_token(self, raw: str) -> dict:
        token_hash = hmac.new(_HMAC_KEY, raw.encode(), hashlib.sha256).hexdigest()
        entry = self._tokens.get(token_hash)
        if not entry:
            return {"status": "not_found"}
        entry["revoked"] = True
        return {"status": "revoked", "name": entry["name"]}

    def list_tokens(self) -> list[dict]:
        return [{"name": v["name"], "prefix": v["prefix"], "scopes": v["scopes"],
                 "revoked": v["revoked"]} for v in self._tokens.values()]
