"""API playground session — manage interactive API testing sessions."""
from __future__ import annotations
import secrets


class PlaygroundSession:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def create(self, *, user_id: str, base_url: str = "https://api.openskill.io") -> dict:
        sid = f"play_{secrets.token_hex(6)}"
        self._sessions[sid] = {"id": sid, "user_id": user_id, "base_url": base_url,
                                "history": [], "variables": {}}
        return {"session_id": sid, "base_url": base_url}

    def add_request(self, sid: str, *, method: str, path: str, status: int,
                      duration_ms: int) -> dict:
        s = self._sessions.get(sid)
        if not s:
            return {"error": "Session not found"}
        entry = {"method": method, "path": path, "status": status, "duration_ms": duration_ms}
        s["history"].append(entry)
        return {"added": True, "history_count": len(s["history"])}

    def set_variable(self, sid: str, key: str, value: str) -> dict:
        s = self._sessions.get(sid)
        if not s:
            return {"error": "Session not found"}
        s["variables"][key] = value
        return {"set": key, "variables_count": len(s["variables"])}

    def get_session(self, sid: str) -> dict | None:
        return self._sessions.get(sid)
