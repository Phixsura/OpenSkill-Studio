"""Connector OAuth Flow — manage OAuth connections for third-party connectors.

Handles the OAuth handshake between the platform and external services
(Slack, GitHub, etc.) including token storage and refresh.
"""
from __future__ import annotations
import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class OAuthConnection:
    connection_id: str
    connector_id: str
    org_id: str
    provider: str
    status: str = "pending"  # pending, connected, expired, revoked
    access_token_hash: str = ""
    refresh_token_hash: str = ""
    scopes: list[str] = field(default_factory=list)
    expires_at: str = ""
    created_at: str = ""
    last_refreshed: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class ConnectorOAuthFlow:
    """Manages OAuth connections for third-party connectors."""

    def __init__(self):
        self._connections: dict[str, OAuthConnection] = {}
        self._auth_states: dict[str, dict] = {}  # state -> metadata

    def initiate(self, connector_id: str, org_id: str, provider: str,
                 scopes: list[str], redirect_uri: str) -> dict:
        """Start OAuth flow — generate auth URL with state."""
        state = secrets.token_urlsafe(32)
        self._auth_states[state] = {
            "connector_id": connector_id, "org_id": org_id,
            "provider": provider, "scopes": scopes,
            "redirect_uri": redirect_uri,
        }
        return {
            "auth_url": f"https://{provider}.com/oauth/authorize?state={state}&scope={'+'.join(scopes)}",
            "state": state,
        }

    def complete(self, state: str, auth_code: str) -> tuple[OAuthConnection | None, str]:
        """Complete OAuth flow with auth code."""
        meta = self._auth_states.pop(state, None)
        if not meta:
            return None, "Invalid or expired state"

        conn_id = f"conn-{secrets.token_urlsafe(8)}"
        connection = OAuthConnection(
            connection_id=conn_id,
            connector_id=meta["connector_id"],
            org_id=meta["org_id"],
            provider=meta["provider"],
            status="connected",
            access_token_hash=f"hash_{auth_code[:8]}",
            scopes=meta["scopes"],
        )
        self._connections[conn_id] = connection
        return connection, "Connected"

    def refresh(self, connection_id: str) -> tuple[bool, str]:
        """Refresh an expired connection."""
        conn = self._connections.get(connection_id)
        if not conn:
            return False, "Connection not found"
        if conn.status == "revoked":
            return False, "Connection revoked — re-authorize required"
        conn.status = "connected"
        conn.last_refreshed = datetime.now(timezone.utc).isoformat()
        conn.access_token_hash = f"refreshed_{secrets.token_urlsafe(4)}"
        return True, "Refreshed"

    def revoke(self, connection_id: str) -> bool:
        conn = self._connections.get(connection_id)
        if conn:
            conn.status = "revoked"
            conn.access_token_hash = ""
            conn.refresh_token_hash = ""
            return True
        return False

    def get_connection(self, connection_id: str) -> OAuthConnection | None:
        return self._connections.get(connection_id)

    def list_connections(self, org_id: str, provider: str | None = None) -> list[OAuthConnection]:
        conns = [c for c in self._connections.values() if c.org_id == org_id]
        if provider:
            conns = [c for c in conns if c.provider == provider]
        return conns

    def is_connected(self, org_id: str, connector_id: str) -> bool:
        return any(
            c.org_id == org_id and c.connector_id == connector_id and c.status == "connected"
            for c in self._connections.values()
        )
