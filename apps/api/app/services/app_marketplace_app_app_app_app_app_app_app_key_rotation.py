"""API key rotation scheduler — schedule and track key rotations."""
from __future__ import annotations
import time, secrets, hashlib


class KeyRotationScheduler:
    def __init__(self, rotation_days: int = 90):
        self._rotation_days = rotation_days
        self._keys: dict[str, dict] = {}

    def register_key(self, name: str, created_days_ago: int = 0) -> dict:
        age = created_days_ago
        due_in = max(0, self._rotation_days - age)
        overdue = age > self._rotation_days
        self._keys[name] = {"name": name, "age_days": age, "due_in_days": due_in,
                             "overdue": overdue, "rotated": False}
        return self._keys[name]

    def rotate(self, name: str) -> dict:
        key = self._keys[name]
        old_age = key["age_days"]
        key["age_days"] = 0
        key["due_in_days"] = self._rotation_days
        key["overdue"] = False
        key["rotated"] = True
        return {"name": name, "rotated": True, "old_age_days": old_age}

    def overdue_keys(self) -> list[dict]:
        return sorted([k for k in self._keys.values() if k["overdue"]],
                       key=lambda k: -k["age_days"])

    def stats(self) -> dict:
        overdue = sum(1 for k in self._keys.values() if k["overdue"])
        return {"total_keys": len(self._keys), "overdue": overdue,
                "rotation_days": self._rotation_days}
