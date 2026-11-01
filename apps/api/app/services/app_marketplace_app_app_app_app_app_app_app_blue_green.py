"""Blue-green deployment switcher — manage blue/green slot switching."""
from __future__ import annotations


class BlueGreenDeployer:
    def __init__(self):
        self._active = "blue"
        self._slots = {
            "blue": {"version": "", "healthy": False},
            "green": {"version": "", "healthy": False},
        }

    def deploy_to_inactive(self, version: str) -> dict:
        inactive = "green" if self._active == "blue" else "blue"
        self._slots[inactive] = {"version": version, "healthy": False}
        return {"slot": inactive, "version": version, "status": "deploying"}

    def mark_healthy(self, slot: str) -> dict:
        self._slots[slot]["healthy"] = True
        return {"slot": slot, "healthy": True}

    def switch(self) -> dict:
        inactive = "green" if self._active == "blue" else "blue"
        if not self._slots[inactive]["healthy"]:
            return {"success": False, "reason": "inactive_slot_unhealthy"}
        old_active = self._active
        self._active = inactive
        return {"success": True, "old_active": old_active,
                "new_active": self._active,
                "version": self._slots[self._active]["version"]}

    def status(self) -> dict:
        return {"active": self._active, "slots": dict(self._slots)}
