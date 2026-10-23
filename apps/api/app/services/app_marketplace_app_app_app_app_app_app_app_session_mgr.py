"""User session manager — track active sessions and enforce limits."""
from __future__ import annotations
import secrets
import time


class SessionManager:
    def __init__(self, *, max_sessions_per_user: int = 5):
        self._sessions: dict[str, dict] = {}
        self._max = max_sessions_per_user

    def create(self, *, user_id: str, ip: str = "", user_agent: str = "",
               now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        user_sessions = [s for s in self._sessions.values() if s["user_id"] == user_id]
        if len(user_sessions) >= self._max:
            oldest = min(user_sessions, key=lambda s: s["created"])
            del self._sessions[oldest["id"]]
        sid = f"sess_{secrets.token_hex(12)}"
        self._sessions[sid] = {"id": sid, "user_id": user_id, "ip": ip,
                                "user_agent": user_agent, "created": ts, "last_active": ts}
        return {"session_id": sid, "user_id": user_id}

    def touch(self, sid: str, *, now: float | None = None) -> dict:
        s = self._sessions.get(sid)
        if not s:
            return {"error": "Session not found"}
        s["last_active"] = now if now is not None else time.time()
        return {"touched": True}

    def revoke(self, sid: str) -> dict:
        if sid in self._sessions:
            del self._sessions[sid]
            return {"revoked": True}
        return {"revoked": False}

    def user_sessions(self, user_id: str) -> list[dict]:
        return [{"id": s["id"], "ip": s["ip"], "user_agent": s["user_agent"][:50]}
                for s in self._sessions.values() if s["user_id"] == user_id]

    def stats(self) -> dict:
        return {"total_sessions": len(self._sessions),
                "unique_users": len({s["user_id"] for s in self._sessions.values()})}
