"""API key rotation scheduler — schedule and execute key rotations."""
from __future__ import annotations
import secrets
import time


class KeyRotationScheduler:
    def __init__(self):
        self._keys: dict[str, dict] = {}

    def register_key(self, key_id: str, *, rotation_days: int = 90) -> dict:
        now = time.time()
        self._keys[key_id] = {
            "created": now, "last_rotated": now,
            "rotation_days": rotation_days,
            "current": secrets.token_urlsafe(24),
            "previous": None, "rotations": 0,
        }
        return {"key_id": key_id, "rotation_days": rotation_days, "status": "registered"}

    def check_rotation(self, key_id: str, *, now: float | None = None) -> dict:
        ts = now if now is not None else time.time()
        entry = self._keys.get(key_id)
        if not entry:
            return {"error": "Key not found"}
        days_since = (ts - entry["last_rotated"]) / 86400
        due = days_since >= entry["rotation_days"]
        days_left = max(0, entry["rotation_days"] - days_since)
        return {"key_id": key_id, "days_since_rotation": round(days_since, 1),
                "days_until_due": round(days_left, 1), "due": due,
                "urgency": "overdue" if days_since > entry["rotation_days"] * 1.1 else "due" if due else "ok"}

    def rotate(self, key_id: str) -> dict:
        entry = self._keys.get(key_id)
        if not entry:
            return {"error": "Key not found"}
        entry["previous"] = entry["current"]
        entry["current"] = secrets.token_urlsafe(24)
        entry["last_rotated"] = time.time()
        entry["rotations"] += 1
        return {"key_id": key_id, "rotated": True, "rotations": entry["rotations"]}

    def summary(self) -> dict:
        total = len(self._keys)
        due = sum(1 for k in self._keys if self.check_rotation(k).get("due"))
        return {"total_keys": total, "due_for_rotation": due, "healthy": due == 0}
