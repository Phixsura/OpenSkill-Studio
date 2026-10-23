"""OAuth2 client manager — register and manage OAuth2 client credentials."""
from __future__ import annotations
import secrets
import hmac
import hashlib

_HMAC_KEY = secrets.token_bytes(32)


class OAuth2ClientManager:
    def __init__(self):
        self._clients: dict[str, dict] = {}

    def register(self, *, name: str, redirect_uris: list[str],
                  scopes: list[str], grant_types: list[str] | None = None) -> dict:
        client_id = f"osk_{secrets.token_hex(12)}"
        client_secret = secrets.token_urlsafe(32)
        secret_hash = hmac.new(_HMAC_KEY, client_secret.encode(), hashlib.sha256).hexdigest()
        self._clients[client_id] = {
            "name": name, "redirect_uris": redirect_uris, "scopes": scopes,
            "grant_types": grant_types or ["authorization_code"],
            "secret_hash": secret_hash, "active": True,
        }
        return {"client_id": client_id, "client_secret": client_secret,
                "name": name, "scopes": scopes}

    def validate(self, client_id: str, client_secret: str) -> dict:
        client = self._clients.get(client_id)
        if not client:
            return {"valid": False, "reason": "client_not_found"}
        if not client["active"]:
            return {"valid": False, "reason": "client_disabled"}
        expected = hmac.new(_HMAC_KEY, client_secret.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, client["secret_hash"]):
            return {"valid": False, "reason": "invalid_secret"}
        return {"valid": True, "name": client["name"], "scopes": client["scopes"]}

    def revoke(self, client_id: str) -> dict:
        client = self._clients.get(client_id)
        if not client:
            return {"status": "not_found"}
        client["active"] = False
        return {"status": "revoked", "client_id": client_id}

    def list_clients(self) -> list[dict]:
        return [{"client_id": cid, "name": c["name"], "scopes": c["scopes"],
                 "active": c["active"]} for cid, c in self._clients.items()]
