"""App API Playground Session — manage interactive API session state.

Manages playground sessions:
- Create sessions with auth context
- Store request/response history per session
- Session timeout management
- Per-installation scoped sessions
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class SessionRequest:
    """A request in a playground session."""

    method: str
    path: str
    status_code: int
    duration_ms: float


@dataclass
class PlaygroundSession:
    """An interactive playground session."""

    session_id: str
    user_id: str
    history: list[SessionRequest] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    expires_at: float = 0.0
    active: bool = True

    @property
    def request_count(self) -> int:
        return len(self.history)

    @property
    def is_expired(self) -> bool:
        return self.expires_at > 0 and time.time() > self.expires_at


class AppAPIPlaygroundSession:
    """Manage interactive API session state."""

    def __init__(self, default_ttl: int = 3600) -> None:
        self._ttl = default_ttl
        self._sessions: dict[tuple[str, str], PlaygroundSession] = {}

    def create(
        self, installation_id: str, session_id: str, user_id: str,
    ) -> PlaygroundSession:
        if not installation_id:
            raise ValueError("installation_id is required")

        key = (installation_id, session_id)
        if key in self._sessions:
            raise ValueError(f"Session {session_id} already exists")

        session = PlaygroundSession(
            session_id=session_id, user_id=user_id,
            expires_at=time.time() + self._ttl,
        )
        self._sessions[key] = session
        return session

    def add_request(
        self, installation_id: str, session_id: str, user_id: str,
        method: str, path: str, status_code: int, duration_ms: float,
    ) -> PlaygroundSession:
        s = self._get(installation_id, session_id)
        if s.user_id != user_id:
            raise ValueError("Not session owner")
        if not s.active or s.is_expired:
            raise ValueError("Session expired or inactive")
        s.history.append(SessionRequest(
            method=method.upper(), path=path,
            status_code=status_code, duration_ms=duration_ms,
        ))
        return s

    def end(self, installation_id: str, session_id: str, user_id: str) -> PlaygroundSession:
        s = self._get(installation_id, session_id)
        if s.user_id != user_id:
            raise ValueError("Not session owner")
        s.active = False
        return s

    def active_sessions(self, installation_id: str) -> list[PlaygroundSession]:
        return [
            s for (inst, _), s in self._sessions.items()
            if inst == installation_id and s.active and not s.is_expired
        ]

    def list_sessions(self, installation_id: str) -> list[PlaygroundSession]:
        return [s for (inst, _), s in self._sessions.items() if inst == installation_id]

    def _get(self, installation_id: str, session_id: str) -> PlaygroundSession:
        key = (installation_id, session_id)
        s = self._sessions.get(key)
        if s is None:
            raise KeyError(f"Session {session_id} not found")
        return s
