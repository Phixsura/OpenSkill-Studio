"""App API OAuth Client — manage OAuth2 client credentials.

Manages OAuth clients:
- Register clients with redirect URIs
- Generate client ID and secret
- Track grant types
- Per-installation scoped clients
"""

from __future__ import annotations

import hashlib
import secrets
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class OAuthClient:
    """An OAuth2 client."""

    client_id: str
    client_name: str
    secret_hash: str
    redirect_uris: list[str]
    grant_types: list[str] = field(default_factory=lambda: ["authorization_code"])
    active: bool = True


VALID_GRANTS = {"authorization_code", "client_credentials", "refresh_token"}


class AppAPIOAuthClient:
    """Manage OAuth2 client credentials."""

    def __init__(self) -> None:
        self._clients: dict[tuple[str, str], OAuthClient] = {}

    def register(
        self, installation_id: str, client_name: str,
        redirect_uris: list[str], grant_types: list[str] | None = None,
    ) -> tuple[OAuthClient, str]:
        """Register client. Returns (client, raw_secret)."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not redirect_uris:
            raise ValueError("at least one redirect_uri required")

        grants = grant_types or ["authorization_code"]
        for g in grants:
            if g not in VALID_GRANTS:
                raise ValueError(f"Invalid grant type: {g}")

        client_id = f"oc_{secrets.token_urlsafe(16)}"
        raw_secret = secrets.token_urlsafe(32)
        secret_hash = hashlib.sha256(raw_secret.encode()).hexdigest()

        client = OAuthClient(
            client_id=client_id, client_name=client_name,
            secret_hash=secret_hash, redirect_uris=redirect_uris,
            grant_types=grants,
        )
        self._clients[(installation_id, client_id)] = client
        return client, raw_secret

    def verify_secret(self, installation_id: str, client_id: str, raw_secret: str) -> bool:
        key = (installation_id, client_id)
        client = self._clients.get(key)
        if client is None or not client.active:
            return False
        return client.secret_hash == hashlib.sha256(raw_secret.encode()).hexdigest()

    def deactivate(self, installation_id: str, client_id: str) -> OAuthClient:
        key = (installation_id, client_id)
        c = self._clients.get(key)
        if c is None:
            raise KeyError(f"Client {client_id} not found")
        c.active = False
        return c

    def list_clients(self, installation_id: str) -> list[OAuthClient]:
        return [c for (inst, _), c in self._clients.items() if inst == installation_id]
