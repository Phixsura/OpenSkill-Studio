"""Blue-green deployment switcher — zero-downtime deployments."""
from __future__ import annotations


class BlueGreenSwitcher:
    def __init__(self):
        self._slots = {
            "blue": {"version": "", "status": "idle", "health": "unknown"},
            "green": {"version": "", "status": "idle", "health": "unknown"},
        }
        self._active = "blue"

    def deploy(self, *, version: str) -> dict:
        inactive = "green" if self._active == "blue" else "blue"
        self._slots[inactive]["version"] = version
        self._slots[inactive]["status"] = "deploying"
        return {"slot": inactive, "version": version, "status": "deploying"}

    def health_check(self, slot: str, *, healthy: bool) -> dict:
        s = self._slots.get(slot)
        if not s:
            return {"error": "Invalid slot"}
        s["health"] = "healthy" if healthy else "unhealthy"
        s["status"] = "ready" if healthy else "failed"
        return {"slot": slot, "health": s["health"], "status": s["status"]}

    def switch(self) -> dict:
        inactive = "green" if self._active == "blue" else "blue"
        if self._slots[inactive]["status"] != "ready":
            return {"error": f"Slot {inactive} is not ready (status: {self._slots[inactive]['status']})"}
        old = self._active
        self._active = inactive
        self._slots[old]["status"] = "idle"
        self._slots[inactive]["status"] = "active"
        return {"switched_to": inactive, "previous": old,
                "version": self._slots[inactive]["version"]}

    def rollback(self) -> dict:
        inactive = "green" if self._active == "blue" else "blue"
        if not self._slots[inactive]["version"]:
            return {"error": "No previous version to rollback to"}
        old = self._active
        self._active = inactive
        self._slots[old]["status"] = "idle"
        self._slots[inactive]["status"] = "active"
        return {"rolled_back_to": inactive, "version": self._slots[inactive]["version"]}

    def status(self) -> dict:
        return {"active": self._active, "slots": dict(self._slots),
                "active_version": self._slots[self._active]["version"]}
