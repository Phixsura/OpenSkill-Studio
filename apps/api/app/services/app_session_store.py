"""App Session Store — manage user sessions for installed apps.

Tracks user sessions with expiry and metadata:
- Create/get/revoke sessions
- TTL-based expiry
- Session data storage
- Per-installation scoped sessions
- Active session listing per user
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()

DEFAULT_TTL_SECONDS = 3600  # 1 hour


@dataclass
class Session:
    """A user session."""

    session_id: str
    installation_id: str
    user_id: str
    token: str
    data: dict = field(default_factory=dict)
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    last_accessed_at: float = field(default_factory=time.time)
    revoked: bool = False


class AppSessionStore:
    """Manage user sessions for installed apps."""

    def __init__(self, ttl_seconds: int = DEFAULT_TTL_SECONDS) -> None:
        if ttl_seconds < 1:
            raise ValueError("ttl_seconds must be >= 1")
        self._ttl = ttl_seconds
        # (installation_id, session_id) → Session
        self._sessions: dict[tuple[str, str], Session] = {}
        # token → (installation_id, session_id) for lookup
        self._token_index: dict[str, tuple[str, str]] = {}

    def create_session(
        self,
        installation_id: str,
        session_id: str,
        user_id: str,
        data: dict | None = None,
        now: float | None = None,
    ) -> Session:
        """Create a new session."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not session_id:
            raise ValueError("session_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        key = (installation_id, session_id)
        if key in self._sessions:
            raise ValueError(f"Session {session_id} already exists")

        now = now or time.time()
        token = secrets.token_urlsafe(32)
        session = Session(
            session_id=session_id,
            installation_id=installation_id,
            user_id=user_id,
            token=token,
            data=data or {},
            created_at=now,
            expires_at=now + self._ttl,
            last_accessed_at=now,
        )
        self._sessions[key] = session
        self._token_index[token] = key
        return session

    def get_by_token(
        self, token: str, now: float | None = None
    ) -> Session | None:
        """Get a session by token. Returns None if expired or revoked."""
        now = now or time.time()
        key = self._token_index.get(token)
        if key is None:
            return None
        session = self._sessions.get(key)
        if session is None:
            return None
        if session.revoked or now >= session.expires_at:
            return None
        session.last_accessed_at = now
        return session

    def get_session(
        self, installation_id: str, session_id: str, now: float | None = None
    ) -> Session:
        """Get a session by ID."""
        key = (installation_id, session_id)
        session = self._sessions.get(key)
        if session is None:
            raise KeyError(f"Session {session_id} not found")
        return session

    def revoke_session(self, installation_id: str, session_id: str) -> Session:
        """Revoke a session."""
        session = self.get_session(installation_id, session_id)
        session.revoked = True
        return session

    def revoke_user_sessions(self, installation_id: str, user_id: str) -> int:
        """Revoke all sessions for a user. Returns count."""
        count = 0
        for (inst, _), session in self._sessions.items():
            if inst == installation_id and session.user_id == user_id and not session.revoked:
                session.revoked = True
                count += 1
        return count

    def update_data(
        self, installation_id: str, session_id: str, data: dict
    ) -> Session:
        """Update session data."""
        session = self.get_session(installation_id, session_id)
        if session.revoked:
            raise ValueError("Cannot update revoked session")
        session.data.update(data)
        return session

    def list_user_sessions(
        self, installation_id: str, user_id: str, active_only: bool = True,
        now: float | None = None,
    ) -> list[Session]:
        """List sessions for a user."""
        now = now or time.time()
        results = []
        for (inst, _), session in self._sessions.items():
            if inst != installation_id or session.user_id != user_id:
                continue
            if active_only and (session.revoked or now >= session.expires_at):
                continue
            results.append(session)
        return results

    def cleanup_expired(self, now: float | None = None) -> int:
        """Remove expired sessions. Returns count."""
        now = now or time.time()
        expired = [
            k for k, s in self._sessions.items()
            if now >= s.expires_at or s.revoked
        ]
        for k in expired:
            session = self._sessions.pop(k)
            self._token_index.pop(session.token, None)
        return len(expired)
