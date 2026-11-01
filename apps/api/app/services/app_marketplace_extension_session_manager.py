"""Session Manager — manage developer sessions and active connections.

Tracks active developer sessions, enforces concurrent session limits,
handles session expiry, and provides session analytics.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field


@dataclass
class Session:
    session_id: str
    developer_id: str
    ip_address: str
    user_agent: str
    created_at: float
    last_active: float
    ttl_seconds: float = 3600.0
    active: bool = True

    @property
    def expired(self) -> bool:
        return time.monotonic() - self.last_active > self.ttl_seconds


class SessionManager:
    """Manages developer sessions with limits and expiry."""

    def __init__(self, max_sessions_per_user: int = 5, default_ttl: float = 3600.0):
        self._sessions: dict[str, Session] = {}
        self._user_sessions: dict[str, list[str]] = {}
        self._max_per_user = max_sessions_per_user
        self._default_ttl = default_ttl

    def create(self, developer_id: str, ip: str = "", user_agent: str = "") -> tuple[Session | None, str]:
        """Create a new session. Enforces max concurrent sessions."""
        self._cleanup_expired(developer_id)
        user_sids = self._user_sessions.get(developer_id, [])
        active = [sid for sid in user_sids if sid in self._sessions and self._sessions[sid].active]

        if len(active) >= self._max_per_user:
            return None, f"Max {self._max_per_user} concurrent sessions reached"

        session_id = f"sess_{secrets.token_urlsafe(16)}"
        now = time.monotonic()
        session = Session(session_id, developer_id, ip, user_agent, now, now, self._default_ttl)
        self._sessions[session_id] = session
        self._user_sessions.setdefault(developer_id, []).append(session_id)
        return session, "Created"

    def validate(self, session_id: str) -> tuple[bool, Session | None]:
        """Validate and refresh a session."""
        session = self._sessions.get(session_id)
        if not session or not session.active:
            return False, None
        if session.expired:
            session.active = False
            return False, None
        session.last_active = time.monotonic()
        return True, session

    def revoke(self, session_id: str) -> bool:
        session = self._sessions.get(session_id)
        if session:
            session.active = False
            return True
        return False

    def revoke_all(self, developer_id: str) -> int:
        """Revoke all sessions for a developer."""
        count = 0
        for sid in self._user_sessions.get(developer_id, []):
            session = self._sessions.get(sid)
            if session and session.active:
                session.active = False
                count += 1
        return count

    def get_active_sessions(self, developer_id: str) -> list[Session]:
        self._cleanup_expired(developer_id)
        return [
            self._sessions[sid] for sid in self._user_sessions.get(developer_id, [])
            if sid in self._sessions and self._sessions[sid].active and not self._sessions[sid].expired
        ]

    def get_stats(self) -> dict:
        active = sum(1 for s in self._sessions.values() if s.active and not s.expired)
        return {
            "total_sessions": len(self._sessions),
            "active": active,
            "unique_developers": len(self._user_sessions),
        }

    def _cleanup_expired(self, developer_id: str) -> None:
        for sid in list(self._user_sessions.get(developer_id, [])):
            session = self._sessions.get(sid)
            if session and session.expired:
                session.active = False
