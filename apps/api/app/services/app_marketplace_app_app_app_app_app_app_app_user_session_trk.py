"""User session tracker — track active user sessions."""
from __future__ import annotations
import secrets
import time

_sessions: dict[str, dict] = {}


def create_session(user_id: str, ip: str, user_agent: str = "", ttl_sec: int = 3600) -> dict:
    sid = f"sess_{secrets.token_urlsafe(16)}"
    _sessions[sid] = {"session_id": sid, "user_id": user_id, "ip": ip,
                       "user_agent": user_agent, "created_at": time.time(),
                       "expires_at": time.time() + ttl_sec, "active": True}
    return _sessions[sid]


def get_active(user_id: str) -> list[dict]:
    now = time.time()
    return [s for s in _sessions.values()
            if s["user_id"] == user_id and s["active"] and now < s["expires_at"]]


def revoke_session(session_id: str) -> dict:
    s = _sessions.get(session_id)
    if not s:
        return {"revoked": False, "error": "not_found"}
    s["active"] = False
    return {"revoked": True, "session_id": session_id}


def session_stats() -> dict:
    now = time.time()
    active = sum(1 for s in _sessions.values() if s["active"] and now < s["expires_at"])
    expired = sum(1 for s in _sessions.values() if now >= s["expires_at"])
    users = len({s["user_id"] for s in _sessions.values() if s["active"] and now < s["expires_at"]})
    return {"total": len(_sessions), "active": active, "expired": expired, "unique_users": users}


def clear_sessions() -> None:
    _sessions.clear()
