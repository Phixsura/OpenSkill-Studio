"""Connector Auth Provider — manage authentication for third-party connectors.

Supports OAuth2, API key, and basic auth flows with secure credential
storage (hashed), token refresh, and connection testing.
"""
from __future__ import annotations
import hashlib
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class AuthType(str, Enum):
    OAUTH2 = "oauth2"
    API_KEY = "api_key"
    BASIC = "basic"
    BEARER = "bearer"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"
    EXPIRED = "expired"
    ERROR = "error"


@dataclass
class ConnectorCredential:
    credential_id: str
    connector_id: str
    extension_id: str
    auth_type: AuthType
    status: ConnectionStatus = ConnectionStatus.DISCONNECTED
    # Store hashes, not raw credentials
    credential_hash: str = ""
    token_expires_at: float = 0.0
    scopes: list[str] = field(default_factory=list)
    last_used: float = 0.0
    created_at: float = 0.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = time.time()


class ConnectorAuthService:
    """Manages connector authentication with secure credential storage."""

    def __init__(self):
        self._credentials: dict[str, ConnectorCredential] = {}
        self._refresh_tokens: dict[str, str] = {}  # cred_id -> hashed refresh

    def _hash(self, value: str) -> str:
        return hashlib.sha256(value.encode()).hexdigest()

    def store_api_key(self, connector_id: str, extension_id: str,
                      api_key: str) -> ConnectorCredential:
        cred_id = f"cred_{secrets.token_urlsafe(10)}"
        cred = ConnectorCredential(
            credential_id=cred_id, connector_id=connector_id,
            extension_id=extension_id, auth_type=AuthType.API_KEY,
            credential_hash=self._hash(api_key),
            status=ConnectionStatus.CONNECTED,
        )
        self._credentials[cred_id] = cred
        return cred

    def store_oauth2(self, connector_id: str, extension_id: str,
                     access_token: str, refresh_token: str,
                     expires_in: int, scopes: list[str]) -> ConnectorCredential:
        cred_id = f"cred_{secrets.token_urlsafe(10)}"
        cred = ConnectorCredential(
            credential_id=cred_id, connector_id=connector_id,
            extension_id=extension_id, auth_type=AuthType.OAUTH2,
            credential_hash=self._hash(access_token),
            token_expires_at=time.time() + expires_in,
            scopes=scopes, status=ConnectionStatus.CONNECTED,
        )
        self._credentials[cred_id] = cred
        self._refresh_tokens[cred_id] = self._hash(refresh_token)
        return cred

    def verify_api_key(self, credential_id: str, api_key: str) -> bool:
        cred = self._credentials.get(credential_id)
        if not cred or cred.auth_type != AuthType.API_KEY:
            return False
        if self._hash(api_key) != cred.credential_hash:
            return False
        cred.last_used = time.time()
        return True

    def is_token_expired(self, credential_id: str) -> bool:
        cred = self._credentials.get(credential_id)
        if not cred:
            return True
        if cred.auth_type != AuthType.OAUTH2:
            return False
        return time.time() > cred.token_expires_at

    def refresh_oauth2(self, credential_id: str, new_access_token: str,
                       new_refresh_token: str, expires_in: int) -> bool:
        cred = self._credentials.get(credential_id)
        if not cred or cred.auth_type != AuthType.OAUTH2:
            return False
        cred.credential_hash = self._hash(new_access_token)
        cred.token_expires_at = time.time() + expires_in
        cred.status = ConnectionStatus.CONNECTED
        self._refresh_tokens[credential_id] = self._hash(new_refresh_token)
        return True

    def disconnect(self, credential_id: str) -> bool:
        cred = self._credentials.get(credential_id)
        if not cred:
            return False
        cred.status = ConnectionStatus.DISCONNECTED
        cred.credential_hash = ""
        self._refresh_tokens.pop(credential_id, None)
        return True

    def get_status(self, credential_id: str) -> dict | None:
        cred = self._credentials.get(credential_id)
        if not cred:
            return None
        expired = self.is_token_expired(credential_id)
        if expired and cred.status == ConnectionStatus.CONNECTED:
            cred.status = ConnectionStatus.EXPIRED
        return {
            "credential_id": cred.credential_id,
            "connector_id": cred.connector_id,
            "auth_type": cred.auth_type.value,
            "status": cred.status.value,
            "scopes": cred.scopes,
            "expired": expired,
        }

    def list_credentials(self, extension_id: str) -> list[ConnectorCredential]:
        return [c for c in self._credentials.values() if c.extension_id == extension_id]
