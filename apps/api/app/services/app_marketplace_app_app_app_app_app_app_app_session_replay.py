"""Session replay recorder — capture and replay user sessions."""
from __future__ import annotations
import html


class SessionReplayRecorder:
    def __init__(self):
        self._sessions: dict[str, dict] = {}

    def start(self, session_id: str, *, user_id: str, page: str) -> dict:
        self._sessions[session_id] = {
            "user_id": user_id, "start_page": html.escape(page),
            "events": [], "duration_ms": 0, "error_count": 0,
        }
        return {"session_id": session_id, "status": "recording"}

    def record_event(self, session_id: str, *, event_type: str,
                      target: str = "", timestamp_ms: int = 0) -> dict:
        s = self._sessions.get(session_id)
        if not s:
            return {"error": "Session not found"}
        evt = {"type": event_type, "target": html.escape(target),
               "timestamp_ms": timestamp_ms}
        s["events"].append(evt)
        if event_type == "error":
            s["error_count"] += 1
        if timestamp_ms > s["duration_ms"]:
            s["duration_ms"] = timestamp_ms
        return {"recorded": True, "total_events": len(s["events"])}

    def get_replay(self, session_id: str) -> dict:
        s = self._sessions.get(session_id)
        if not s:
            return {"error": "Session not found"}
        return {
            "session_id": session_id,
            "user_id": s["user_id"],
            "start_page": s["start_page"],
            "duration_ms": s["duration_ms"],
            "duration_display": f"{s['duration_ms'] / 1000:.1f}s",
            "total_events": len(s["events"]),
            "error_count": s["error_count"],
            "events": s["events"],
            "has_errors": s["error_count"] > 0,
        }
