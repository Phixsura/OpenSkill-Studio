"""Consumer API Session Manager — manage authenticated API sessions."""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import secrets
import hashlib
import structlog

log = structlog.get_logger()

@dataclass
class APISession:
    session_id: str
    consumer_id: str
    token_hash: str
    ip_address: str = ""
    user_agent: str = ""
    created_at: datetime | None = None
    last_active_at: datetime | None = None
    expires_at: datetime | None = None
    revoked: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiSessionManager:
    def __init__(self, session_ttl_hours: int = 24, max_sessions: int = 10) -> None:
        self._sessions: dict[tuple[str, str], APISession] = {}
        self._ttl_hours = session_ttl_hours
        self._max = max_sessions

    def create(self, installation_id: str, consumer_id: str, ip: str = "", user_agent: str = "", now: datetime | None = None) -> tuple[str, APISession]:
        if not installation_id:
            raise ValueError("installation_id is required")
        now = now or datetime.utcnow()
        token = secrets.token_urlsafe(32)
        session = APISession(
            session_id=hashlib.sha256(token.encode()).hexdigest()[:16],
            consumer_id=consumer_id, token_hash=hashlib.sha256(token.encode()).hexdigest(),
            ip_address=ip, user_agent=user_agent,
            created_at=now, last_active_at=now,
            expires_at=now + timedelta(hours=self._ttl_hours),
        )
        key = (installation_id, session.session_id)
        # Enforce max sessions
        consumer_sessions = [(k, s) for k, s in self._sessions.items() if k[0] == installation_id and s.consumer_id == consumer_id and not s.revoked]
        if len(consumer_sessions) >= self._max:
            oldest = min(consumer_sessions, key=lambda x: x[1].created_at or datetime.min)
            oldest[1].revoked = True
        self._sessions[key] = session
        return token, session

    def validate(self, installation_id: str, token: str, now: datetime | None = None) -> APISession | None:
        now = now or datetime.utcnow()
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        for (inst, _), s in self._sessions.items():
            if inst == installation_id and s.token_hash == token_hash and not s.revoked:
                if s.expires_at and now >= s.expires_at:
                    return None
                s.last_active_at = now
                return s
        return None

    def revoke(self, installation_id: str, session_id: str) -> APISession:
        key = (installation_id, session_id)
        session = self._sessions.get(key)
        if not session:
            raise ValueError("Session not found")
        session.revoked = True
        return session

    def revoke_all(self, installation_id: str, consumer_id: str) -> int:
        count = 0
        for (inst, _), s in self._sessions.items():
            if inst == installation_id and s.consumer_id == consumer_id and not s.revoked:
                s.revoked = True
                count += 1
        return count

    def active_count(self, installation_id: str, consumer_id: str) -> int:
        return sum(1 for (inst, _), s in self._sessions.items() if inst == installation_id and s.consumer_id == consumer_id and not s.revoked)
