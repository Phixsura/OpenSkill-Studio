"""User session — manage active user sessions and devices."""

import secrets
import hashlib
from datetime import datetime, timedelta


def create_session(*, user_id: str, ip: str, user_agent: str,
                     device_type: str = "desktop") -> dict:
    session_id = secrets.token_urlsafe(24)
    return {
        "session_id": session_id,
        "session_hash": hashlib.sha256(session_id.encode()).hexdigest()[:16],
        "user_id": user_id,
        "ip": ip,
        "user_agent": user_agent,
        "device_type": device_type,
        "created_at": datetime.utcnow().isoformat(),
        "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat(),
        "active": True,
    }


def list_active_sessions(*, sessions: list[dict]) -> dict:
    active = [s for s in sessions if s.get("active")]
    by_device: dict[str, int] = {}
    for s in active:
        dt = s.get("device_type", "unknown")
        by_device[dt] = by_device.get(dt, 0) + 1
    return {"sessions": active, "total_active": len(active), "by_device": by_device}


def revoke_session(*, session_hash: str, sessions: list[dict]) -> dict:
    found = False
    for s in sessions:
        if s.get("session_hash") == session_hash:
            s["active"] = False
            found = True
    if not found:
        return {"error": "Session not found"}
    return {"revoked": True, "session_hash": session_hash}
