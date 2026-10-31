"""Platform session manager — manage user sessions with expiry."""
from __future__ import annotations
import secrets, time


class SessionManager:
    def __init__(self, ttl_seconds: int = 3600):
        self._sessions: dict[str, dict] = {}
        self._ttl = ttl_seconds

    def create(self, user_id: str, metadata: dict | None = None) -> dict:
        token = secrets.token_urlsafe(32)
        self._sessions[token] = {"user_id": user_id, "created_at": time.time(),
                                  "expires_at": time.time() + self._ttl,
                                  "metadata": metadata or {}}
        return {"token": token, "expires_in": self._ttl}

    def validate(self, token: str, now: float | None = None) -> dict:
        now = now or time.time()
        session = self._sessions.get(token)
        if not session:
            return {"valid": False, "reason": "not_found"}
        if now > session["expires_at"]:
            del self._sessions[token]
            return {"valid": False, "reason": "expired"}
        return {"valid": True, "user_id": session["user_id"],
                "remaining": round(session["expires_at"] - now)}

    def revoke(self, token: str) -> dict:
        if token in self._sessions:
            del self._sessions[token]
            return {"revoked": True}
        return {"revoked": False, "reason": "not_found"}

    def revoke_user(self, user_id: str) -> dict:
        tokens = [t for t, s in self._sessions.items() if s["user_id"] == user_id]
        for t in tokens:
            del self._sessions[t]
        return {"revoked": len(tokens), "user_id": user_id}

    def stats(self) -> dict:
        return {"active_sessions": len(self._sessions), "ttl_seconds": self._ttl}
