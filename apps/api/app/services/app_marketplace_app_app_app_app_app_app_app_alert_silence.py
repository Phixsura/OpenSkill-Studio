"""Alert silence manager — silence alerts during maintenance windows."""
from __future__ import annotations
import time

class AlertSilenceManager:
    def __init__(self):
        self._silences: dict[str, dict] = {}

    def create(self, name: str, matcher: str, duration_minutes: int, reason: str) -> dict:
        self._silences[name] = {"name": name, "matcher": matcher, "reason": reason,
                                 "expires_at": time.time() + duration_minutes * 60,
                                 "duration_minutes": duration_minutes, "active": True}
        return self._silences[name]

    def is_silenced(self, alert_name: str) -> bool:
        now = time.time()
        for s in self._silences.values():
            if s["active"] and now < s["expires_at"] and s["matcher"] in alert_name:
                return True
        return False

    def expire(self, name: str) -> dict:
        self._silences[name]["active"] = False
        return {"name": name, "expired": True}

    def active_count(self) -> int:
        return sum(1 for s in self._silences.values() if s["active"])
