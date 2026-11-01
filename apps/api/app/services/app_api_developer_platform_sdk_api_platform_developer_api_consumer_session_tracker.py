"""API Consumer Session Tracker — track active consumer sessions and connections."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class ConsumerSession:
    session_id: str
    consumer_id: str
    started_at: float = field(default_factory=time.time)
    last_activity: float = field(default_factory=time.time)
    request_count: int = 0
    ip_address: str = ""
    user_agent: str = ""

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiConsumerSessionTracker:
    def __init__(self, idle_timeout_s: int = 1800) -> None:
        self._sessions: dict[tuple[str, str], ConsumerSession] = {}
        self._idle_timeout = max(60, idle_timeout_s)

    def start_session(self, installation_id: str, session: ConsumerSession) -> ConsumerSession:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, session.session_id)
        if key in self._sessions: raise ValueError(f"Session {session.session_id} already exists")
        self._sessions[key] = session
        return session

    def record_activity(self, installation_id: str, session_id: str) -> ConsumerSession:
        key = (installation_id, session_id)
        s = self._sessions.get(key)
        if s is None: raise KeyError(f"Session {session_id} not found")
        s.last_activity = time.time()
        s.request_count += 1
        return s

    def end_session(self, installation_id: str, session_id: str) -> bool:
        key = (installation_id, session_id)
        if key in self._sessions: del self._sessions[key]; return True
        return False

    def active_sessions(self, installation_id: str, consumer_id: str | None = None) -> list[ConsumerSession]:
        now = time.time()
        sessions = [(k, s) for k, s in self._sessions.items() if k[0] == installation_id]
        if consumer_id: sessions = [(k, s) for k, s in sessions if s.consumer_id == consumer_id]
        return [s for _, s in sessions if now - s.last_activity < self._idle_timeout]

    def idle_sessions(self, installation_id: str) -> list[ConsumerSession]:
        now = time.time()
        return [s for (inst, _), s in self._sessions.items()
                if inst == installation_id and now - s.last_activity >= self._idle_timeout]

    def concurrent_count(self, installation_id: str) -> int:
        return len(self.active_sessions(installation_id))

    def unique_consumers(self, installation_id: str) -> int:
        return len({s.consumer_id for (inst, _), s in self._sessions.items() if inst == installation_id})
