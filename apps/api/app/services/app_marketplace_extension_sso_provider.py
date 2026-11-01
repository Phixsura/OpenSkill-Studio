"""Extension SSO Provider — single sign-on for extension ecosystem."""
from __future__ import annotations
from dataclasses import dataclass, field
import secrets
import time
import hashlib


@dataclass
class SSOSession:
    session_id: str
    user_id: str
    extension_id: str
    token: str
    expires_at: float
    created_at: float = 0.0
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtSSOProviderService:
    TOKEN_TTL = 3600  # 1 hour

    def __init__(self):
        self._sessions: dict[str, SSOSession] = {}
        self._trusted_extensions: set[str] = set()

    def trust_extension(self, extension_id: str) -> None:
        self._trusted_extensions.add(extension_id)

    def create_session(self, user_id: str, extension_id: str) -> SSOSession:
        if extension_id not in self._trusted_extensions:
            raise ValueError("Extension not trusted for SSO")
        token = secrets.token_urlsafe(48)
        session = SSOSession(
            session_id=hashlib.sha256(token.encode()).hexdigest()[:16],
            user_id=user_id, extension_id=extension_id, token=token,
            expires_at=time.time() + self.TOKEN_TTL)
        self._sessions[session.session_id] = session
        return session

    def validate(self, token: str) -> SSOSession | None:
        sid = hashlib.sha256(token.encode()).hexdigest()[:16]
        session = self._sessions.get(sid)
        if not session: return None
        if time.time() > session.expires_at:
            del self._sessions[sid]
            return None
        return session

    def revoke(self, session_id: str) -> bool:
        return self._sessions.pop(session_id, None) is not None

    def get_user_sessions(self, user_id: str) -> list[SSOSession]:
        return [s for s in self._sessions.values() if s.user_id == user_id]
