"""Deployment freeze controller — manage deployment freezes during critical periods."""
from __future__ import annotations
import time


class DeployFreezeController:
    def __init__(self):
        self._freezes: list[dict] = []
        self._active_freeze: dict | None = None

    def create_freeze(self, reason: str, duration_hours: int, created_by: str) -> dict:
        freeze = {"reason": reason, "duration_hours": duration_hours,
                  "created_by": created_by, "created_at": time.time(),
                  "expires_at": time.time() + duration_hours * 3600,
                  "active": True}
        self._freezes.append(freeze)
        self._active_freeze = freeze
        return freeze

    def is_frozen(self, now: float | None = None) -> dict:
        now = now or time.time()
        if self._active_freeze and now < self._active_freeze["expires_at"]:
            remaining = round((self._active_freeze["expires_at"] - now) / 3600, 1)
            return {"frozen": True, "reason": self._active_freeze["reason"],
                    "remaining_hours": remaining}
        self._active_freeze = None
        return {"frozen": False}

    def lift_freeze(self) -> dict:
        if self._active_freeze:
            self._active_freeze["active"] = False
            self._active_freeze = None
            return {"lifted": True}
        return {"lifted": False}

    def history(self) -> list[dict]:
        return list(self._freezes)
