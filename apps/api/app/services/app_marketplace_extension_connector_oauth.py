"""Connector OAuth Flow — manage OAuth2 authorization for connectors."""
from __future__ import annotations
from dataclasses import dataclass
import secrets
import time


@dataclass
class OAuthSession:
    session_id: str
    connector_id: str
    user_id: str
    state: str
    redirect_uri: str
    scopes: list[str]
    status: str = "pending"  # pending, authorized, failed, expired
    access_token: str = ""
    refresh_token: str = ""
    expires_at: float = 0.0
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ConnectorOAuthService:
    def __init__(self):
        self._sessions: dict[str, OAuthSession] = {}
        self._tokens: dict[str, OAuthSession] = {}  # user:connector -> session
        self._counter = 0

    def initiate(self, connector_id: str, user_id: str, redirect_uri: str,
                 scopes: list[str]) -> OAuthSession:
        self._counter += 1
        state = secrets.token_urlsafe(32)
        s = OAuthSession(session_id=f"oauth-{self._counter}",
                         connector_id=connector_id, user_id=user_id,
                         state=state, redirect_uri=redirect_uri, scopes=scopes)
        self._sessions[s.session_id] = s
        return s

    def complete(self, session_id: str, state: str) -> OAuthSession | None:
        s = self._sessions.get(session_id)
        if not s or s.state != state or s.status != "pending":
            return None
        s.status = "authorized"
        s.access_token = secrets.token_urlsafe(32)
        s.refresh_token = secrets.token_urlsafe(32)
        s.expires_at = time.time() + 3600
        key = f"{s.user_id}:{s.connector_id}"
        self._tokens[key] = s
        return s

    def get_token(self, user_id: str, connector_id: str) -> str | None:
        key = f"{user_id}:{connector_id}"
        s = self._tokens.get(key)
        if not s: return None
        if s.expires_at != 0 and time.time() > s.expires_at:
            return None  # expired
        return s.access_token

    def revoke(self, user_id: str, connector_id: str) -> bool:
        key = f"{user_id}:{connector_id}"
        s = self._tokens.pop(key, None)
        if s:
            s.status = "expired"
            return True
        return False

    def list_authorized(self, user_id: str) -> list[OAuthSession]:
        return [s for s in self._tokens.values()
                if s.user_id == user_id and s.status == "authorized"]
