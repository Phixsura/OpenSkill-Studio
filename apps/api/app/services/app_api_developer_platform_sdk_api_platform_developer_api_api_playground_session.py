"""API Playground Session — interactive API testing sessions for developers."""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import structlog

log = structlog.get_logger()

@dataclass
class PlaygroundRequest:
    request_id: str
    method: str
    path: str
    headers: dict[str, str] = field(default_factory=dict)
    body: str = ""
    response_status: int = 0
    response_body: str = ""
    duration_ms: float = 0.0
    timestamp: float = field(default_factory=time.time)

@dataclass
class PlaygroundSession:
    session_id: str
    developer_id: str
    api_version: str = "v1"
    requests: list[PlaygroundRequest] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    environment: str = "sandbox"  # "sandbox", "staging"

VALID_ENVS = {"sandbox", "staging"}

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiPlaygroundSession:
    def __init__(self, max_requests_per_session: int = 100) -> None:
        self._sessions: dict[tuple[str, str], PlaygroundSession] = {}
        self._max = max(10, max_requests_per_session)

    def create_session(self, installation_id: str, session: PlaygroundSession) -> PlaygroundSession:
        if not installation_id: raise ValueError("installation_id is required")
        if session.environment not in VALID_ENVS: raise ValueError(f"Invalid environment: {session.environment}")
        key = (installation_id, session.session_id)
        if key in self._sessions: raise ValueError(f"Session {session.session_id} already exists")
        self._sessions[key] = session
        return session

    def add_request(self, installation_id: str, session_id: str, req: PlaygroundRequest) -> PlaygroundRequest:
        key = (installation_id, session_id)
        session = self._sessions.get(key)
        if session is None: raise KeyError(f"Session {session_id} not found")
        if len(session.requests) >= self._max: raise ValueError("Max requests per session reached")
        if len(req.body) > 8192: req.body = req.body[:8192] + "...[TRUNCATED]"
        if len(req.response_body) > 8192: req.response_body = req.response_body[:8192] + "...[TRUNCATED]"
        session.requests.append(req)
        return req

    def get_session(self, installation_id: str, session_id: str) -> PlaygroundSession:
        s = self._sessions.get((installation_id, session_id))
        if s is None: raise KeyError(f"Session {session_id} not found")
        return s

    def list_sessions(self, installation_id: str, developer_id: str | None = None) -> list[PlaygroundSession]:
        sessions = [s for (inst, _), s in self._sessions.items() if inst == installation_id]
        if developer_id: sessions = [s for s in sessions if s.developer_id == developer_id]
        return sessions

    def session_count(self, installation_id: str) -> int:
        return sum(1 for (inst, _) in self._sessions if inst == installation_id)
