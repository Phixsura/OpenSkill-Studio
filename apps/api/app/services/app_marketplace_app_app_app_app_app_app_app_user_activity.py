"""User activity log — track user actions for activity feed and audit."""
from __future__ import annotations
import html
import time


class UserActivityLog:
    def __init__(self):
        self._log: list[dict] = []

    def record(self, *, user_id: str, action: str, resource: str,
                details: str = "", now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        entry = {"user_id": user_id, "action": action,
                 "resource": html.escape(resource), "details": html.escape(details[:300]),
                 "timestamp": ts}
        self._log.append(entry)
        return {"recorded": True}

    def get_feed(self, user_id: str, *, limit: int = 20) -> list[dict]:
        user_entries = [e for e in self._log if e["user_id"] == user_id]
        return list(reversed(user_entries[-limit:]))

    def recent_activity(self, *, limit: int = 50) -> list[dict]:
        return list(reversed(self._log[-limit:]))

    def stats(self, user_id: str) -> dict:
        entries = [e for e in self._log if e["user_id"] == user_id]
        by_action: dict[str, int] = {}
        for e in entries:
            by_action[e["action"]] = by_action.get(e["action"], 0) + 1
        return {"user_id": user_id, "total_actions": len(entries), "by_action": by_action}
