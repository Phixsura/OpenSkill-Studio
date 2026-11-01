"""OAuth Provider — OAuth 2.0 authorization for third-party extensions.

Manages OAuth clients, authorization codes, and access tokens
so extensions can request scoped access to user/org data.
"""
from __future__ import annotations
import hashlib
import secrets
from datetime import datetime, timezone, timedelta


class OAuthProvider:
    """OAuth 2.0 provider for extension authorization."""

    def __init__(self, token_ttl_seconds: int = 3600):
        self._clients: dict[str, dict] = {}
        self._auth_codes: dict[str, dict] = {}
        self._tokens: dict[str, dict] = {}  # token_hash -> token record
        self._token_ttl = token_ttl_seconds

    def register_client(
        self, client_id: str, client_name: str, redirect_uris: list[str],
        scopes: list[str], developer_id: str,
    ) -> dict:
        """Register an OAuth client for an extension."""
        if client_id in self._clients:
            raise ValueError(f"client_id {client_id} already registered")
        client_secret = secrets.token_urlsafe(32)
        client = {
            "client_id": client_id,
            "client_secret_hash": hashlib.sha256(client_secret.encode()).hexdigest(),
            "client_name": client_name,
            "redirect_uris": redirect_uris,
            "scopes": scopes,
            "developer_id": developer_id,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        self._clients[client_id] = client
        return {"client_id": client_id, "client_secret": client_secret, **client}

    def get_client(self, client_id: str) -> dict | None:
        return self._clients.get(client_id)

    def authorize(
        self, client_id: str, user_id: str, scopes: list[str],
        redirect_uri: str,
    ) -> dict | None:
        """Generate an authorization code after user consent."""
        client = self._clients.get(client_id)
        if not client:
            return None
        if redirect_uri not in client["redirect_uris"]:
            return None
        # Validate requested scopes
        invalid = [s for s in scopes if s not in client["scopes"]]
        if invalid:
            return None
        code = secrets.token_urlsafe(32)
        self._auth_codes[code] = {
            "client_id": client_id, "user_id": user_id,
            "scopes": scopes, "redirect_uri": redirect_uri,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "used": False,
        }
        return {"code": code, "redirect_uri": redirect_uri}

    def exchange_code(self, code: str, client_id: str, client_secret: str) -> dict | None:
        """Exchange an authorization code for an access token."""
        auth = self._auth_codes.get(code)
        if not auth or auth["used"] or auth["client_id"] != client_id:
            return None
        client = self._clients.get(client_id)
        if not client:
            return None
        secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
        if secret_hash != client["client_secret_hash"]:
            return None
        auth["used"] = True
        access_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        now = datetime.now(timezone.utc)
        self._tokens[token_hash] = {
            "client_id": client_id, "user_id": auth["user_id"],
            "scopes": auth["scopes"], "created_at": now.isoformat(),
            "expires_at": (now + timedelta(seconds=self._token_ttl)).isoformat(),
        }
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": self._token_ttl,
            "scopes": auth["scopes"],
        }

    def validate_token(self, access_token: str) -> dict | None:
        """Validate an access token and return its claims."""
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        record = self._tokens.get(token_hash)
        if not record:
            return None
        expires = datetime.fromisoformat(record["expires_at"])
        if datetime.now(timezone.utc) > expires:
            return None
        return record

    def revoke_token(self, access_token: str) -> bool:
        token_hash = hashlib.sha256(access_token.encode()).hexdigest()
        return self._tokens.pop(token_hash, None) is not None
