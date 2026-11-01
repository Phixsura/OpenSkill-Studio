"""Consumer OAuth Client — register and manage OAuth2 client credentials."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
import hashlib
import secrets
import structlog

log = structlog.get_logger()

@dataclass
class OAuthClient:
    client_id: str
    consumer_id: str
    client_name: str
    redirect_uris: list[str] = field(default_factory=list)
    scopes: list[str] = field(default_factory=list)
    secret_hash: str = ""
    grant_types: list[str] = field(default_factory=lambda: ["authorization_code"])
    active: bool = True
    created_at: datetime | None = None

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerOauthClient:
    def __init__(self) -> None:
        self._clients: dict[tuple[str, str], OAuthClient] = {}

    def register(self, installation_id: str, client: OAuthClient) -> tuple[str, OAuthClient]:
        if not installation_id:
            raise ValueError("installation_id is required")
        if not client.client_name:
            raise ValueError("client_name is required")
        # Validate redirect URIs are HTTPS
        for uri in client.redirect_uris:
            if not uri.startswith("https://") and not uri.startswith("http://localhost"):
                raise ValueError(f"redirect_uri must be HTTPS: {uri}")
        key = (installation_id, client.client_id)
        if key in self._clients:
            raise ValueError(f"Client {client.client_id} already exists")
        raw_secret = secrets.token_urlsafe(32)
        client.secret_hash = hashlib.sha256(raw_secret.encode()).hexdigest()
        client.created_at = client.created_at or datetime.utcnow()
        self._clients[key] = client
        log.info("oauth_client_registered", installation_id=installation_id, client_id=client.client_id)
        return raw_secret, client

    def authenticate(self, installation_id: str, client_id: str, client_secret: str) -> bool:
        key = (installation_id, client_id)
        client = self._clients.get(key)
        if not client or not client.active:
            return False
        secret_hash = hashlib.sha256(client_secret.encode()).hexdigest()
        return secret_hash == client.secret_hash

    def revoke(self, installation_id: str, client_id: str) -> OAuthClient:
        key = (installation_id, client_id)
        client = self._clients.get(key)
        if not client:
            raise ValueError("Client not found")
        client.active = False
        return client

    def get(self, installation_id: str, client_id: str) -> OAuthClient | None:
        return self._clients.get((installation_id, client_id))

    def list_clients(self, installation_id: str, consumer_id: str) -> list[OAuthClient]:
        return [c for (inst, _), c in self._clients.items() if inst == installation_id and c.consumer_id == consumer_id]
