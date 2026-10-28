"""App Session Manager — manage user sessions.

Manages user sessions:
- Create sessions with TTL
- Validate active sessions
- Revoke sessions (single or all)
- Per-installation scoped sessions
"""

from __future__ import annotations

import secrets
import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class Session:
    """A user session."""

    session_id: str
    user_id: str
    token_hash: str  # stored hash, not raw token
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    revoked: bool = False
    ip_address: str = ""
    user_agent: str = ""

    @property
    def is_active(self) -> bool:
        if self.revoked:
            return False
        if self.expires_at > 0 and time.time() > self.expires_at:
            return False
        return True


class AppSessionManager:
    """Manage user sessions."""

    def __init__(self, default_ttl: int = 3600) -> None:
        self._default_ttl = default_ttl
        self._sessions: dict[tuple[str, str], Session] = {}

    def create(
        self, installation_id: str, user_id: str,
        ttl_seconds: int | None = None, ip_address: str = "",
        user_agent: str = "",
    ) -> tuple[Session, str]:
        """Create a session. Returns (session, raw_token)."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not user_id:
            raise ValueError("user_id is required")

        import hashlib
        raw_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        session_id = secrets.token_urlsafe(16)

        ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
        expires_at = time.time() + ttl if ttl > 0 else 0.0

        session = Session(
            session_id=session_id, user_id=user_id,
            token_hash=token_hash, expires_at=expires_at,
            ip_address=ip_address, user_agent=user_agent,
        )
        self._sessions[(installation_id, session_id)] = session
        return session, raw_token

    def validate(self, installation_id: str, raw_token: str) -> Session | None:
        """Validate a token. Returns session if valid."""
        import hashlib
        token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
        for (inst, _), s in self._sessions.items():
            if inst == installation_id and s.token_hash == token_hash and s.is_active:
                return s
        return None

    def revoke(self, installation_id: str, session_id: str) -> Session:
        key = (installation_id, session_id)
        s = self._sessions.get(key)
        if s is None:
            raise KeyError(f"Session {session_id} not found")
        s.revoked = True
        return s

    def revoke_all(self, installation_id: str, user_id: str) -> int:
        """Revoke all sessions for a user. Returns count."""
        count = 0
        for (inst, _), s in self._sessions.items():
            if inst == installation_id and s.user_id == user_id and not s.revoked:
                s.revoked = True
                count += 1
        return count

    def active_sessions(self, installation_id: str, user_id: str) -> list[Session]:
        return [
            s for (inst, _), s in self._sessions.items()
            if inst == installation_id and s.user_id == user_id and s.is_active
        ]

    def active_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _), s in self._sessions.items() if inst == installation_id and s.is_active)
