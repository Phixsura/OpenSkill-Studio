"""Consumer API Session Analytics — analyze API session patterns."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import structlog

log = structlog.get_logger()

@dataclass
class SessionRecord:
    session_id: str
    consumer_id: str
    started_at: datetime
    ended_at: datetime | None = None
    request_count: int = 0
    endpoints_visited: list[str] = field(default_factory=list)

@dataclass
class SessionAnalytics:
    consumer_id: str
    total_sessions: int
    avg_duration_seconds: float
    avg_requests_per_session: float
    avg_endpoints_per_session: float
    longest_session_seconds: float
    most_visited_endpoint: str

class AppAPIDeveloperPlatformSDKConsumerApiConsumerEndpointApiConsumerSessionAnalytics:
    def __init__(self) -> None:
        self._sessions: dict[tuple[str, str], list[SessionRecord]] = {}

    def record_session(self, installation_id: str, session: SessionRecord) -> SessionRecord:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, session.consumer_id)
        if key not in self._sessions:
            self._sessions[key] = []
        self._sessions[key].append(session)
        if len(self._sessions[key]) > 10000:
            self._sessions[key] = self._sessions[key][-10000:]
        return session

    def get_analytics(self, installation_id: str, consumer_id: str) -> SessionAnalytics:
        sessions = self._sessions.get((installation_id, consumer_id), [])
        if not sessions:
            return SessionAnalytics(consumer_id=consumer_id, total_sessions=0, avg_duration_seconds=0, avg_requests_per_session=0, avg_endpoints_per_session=0, longest_session_seconds=0, most_visited_endpoint="")
        durations = []
        endpoint_counts: dict[str, int] = {}
        for s in sessions:
            if s.ended_at:
                durations.append((s.ended_at - s.started_at).total_seconds())
            for ep in s.endpoints_visited:
                endpoint_counts[ep] = endpoint_counts.get(ep, 0) + 1
        avg_dur = sum(durations) / len(durations) if durations else 0
        longest = max(durations) if durations else 0
        avg_reqs = sum(s.request_count for s in sessions) / len(sessions)
        avg_eps = sum(len(set(s.endpoints_visited)) for s in sessions) / len(sessions)
        most_visited = max(endpoint_counts, key=endpoint_counts.get) if endpoint_counts else ""
        return SessionAnalytics(consumer_id=consumer_id, total_sessions=len(sessions), avg_duration_seconds=round(avg_dur, 1), avg_requests_per_session=round(avg_reqs, 1), avg_endpoints_per_session=round(avg_eps, 1), longest_session_seconds=round(longest, 1), most_visited_endpoint=most_visited)

    def get_active_sessions(self, installation_id: str, consumer_id: str) -> list[SessionRecord]:
        sessions = self._sessions.get((installation_id, consumer_id), [])
        return [s for s in sessions if s.ended_at is None]
