"""API versioning manager — manage multiple API versions with deprecation."""
from __future__ import annotations
import time


class ApiVersionManager:
    def __init__(self):
        self._versions: dict[str, dict] = {}

    def register(self, version: str, status: str = "active", sunset_date: str = "") -> dict:
        self._versions[version] = {"version": version, "status": status,
                                    "sunset_date": sunset_date,
                                    "registered_at": time.time()}
        return self._versions[version]

    def deprecate(self, version: str, sunset_date: str) -> dict:
        v = self._versions[version]
        v["status"] = "deprecated"
        v["sunset_date"] = sunset_date
        return v

    def resolve(self, requested: str) -> dict:
        v = self._versions.get(requested)
        if not v:
            latest = self.latest()
            return {"resolved": latest, "fallback": True}
        if v["status"] == "sunset":
            latest = self.latest()
            return {"resolved": latest, "redirected": True, "reason": "sunset"}
        return {"resolved": requested, "status": v["status"]}

    def latest(self) -> str:
        active = [v for v, d in self._versions.items() if d["status"] == "active"]
        return sorted(active)[-1] if active else ""

    def summary(self) -> dict:
        by_status: dict[str, int] = {}
        for d in self._versions.values():
            by_status[d["status"]] = by_status.get(d["status"], 0) + 1
        return {"total": len(self._versions), "by_status": by_status,
                "latest": self.latest()}
