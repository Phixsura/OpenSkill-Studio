"""App API Developer Consumer Session Tracker — track active consumer sessions."""
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
    last_activity_at: float = field(default_factory=time.time)
    request_count: int = 0
    endpoints_accessed: set[str] = field(default_factory=set)
    active: bool = True

    @property
    def duration_seconds(self) -> float:
        return round(time.time() - self.started_at, 1)

    @property
    def idle_seconds(self) -> float:
        return round(time.time() - self.last_activity_at, 1)

class AppAPIDeveloperPlatformSDKApiConsumerSessionTracker:
    def __init__(self, idle_timeout_seconds: int = 1800) -> None:
        self._idle_timeout = idle_timeout_seconds
        self._sessions: dict[tuple[str, str], ConsumerSession] = {}

    def start(self, installation_id: str, session_id: str, consumer_id: str) -> ConsumerSession:
        if not installation_id: raise ValueError("installation_id is required")
        key = (installation_id, session_id)
        s = ConsumerSession(session_id=session_id, consumer_id=consumer_id)
        self._sessions[key] = s
        return s

    def activity(self, installation_id: str, session_id: str, endpoint: str) -> ConsumerSession:
        key = (installation_id, session_id)
        s = self._sessions.get(key)
        if s is None: raise KeyError(f"Session {session_id} not found")
        s.last_activity_at = time.time()
        s.request_count += 1
        s.endpoints_accessed.add(endpoint)
        return s

    def end(self, installation_id: str, session_id: str) -> ConsumerSession:
        key = (installation_id, session_id)
        s = self._sessions.get(key)
        if s is None: raise KeyError(f"Session {session_id} not found")
        s.active = False
        return s

    def active_sessions(self, installation_id: str) -> list[ConsumerSession]:
        return [s for (inst, _), s in self._sessions.items() if inst == installation_id and s.active]

    def active_count(self, installation_id: str) -> int:
        return len(self.active_sessions(installation_id))

    def by_consumer(self, installation_id: str, consumer_id: str) -> list[ConsumerSession]:
        return [s for (inst, _), s in self._sessions.items() if inst == installation_id and s.consumer_id == consumer_id]
