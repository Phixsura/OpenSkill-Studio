"""API versioning manager — track versions, deprecation, and migration paths."""
from __future__ import annotations


class ApiVersionManager:
    def __init__(self):
        self._versions: dict[str, dict] = {}

    def register_version(self, version: str, *, status: str = "stable",
                          sunset_date: str = "", endpoints: list[str] | None = None) -> dict:
        self._versions[version] = {
            "version": version, "status": status,
            "sunset_date": sunset_date, "endpoints": endpoints or [],
        }
        return {"registered": version, "status": status}

    def deprecate(self, version: str, *, sunset_date: str, migrate_to: str) -> dict:
        v = self._versions.get(version)
        if not v:
            return {"error": f"Version {version} not found"}
        v["status"] = "deprecated"
        v["sunset_date"] = sunset_date
        v["migrate_to"] = migrate_to
        return {"deprecated": version, "sunset_date": sunset_date, "migrate_to": migrate_to}

    def resolve(self, requested: str) -> dict:
        v = self._versions.get(requested)
        if not v:
            latest = self.latest()
            return {"resolved": latest, "reason": "version_not_found", "fallback": True}
        if v["status"] == "deprecated":
            return {"resolved": requested, "status": "deprecated",
                    "warning": f"Version {requested} is deprecated. Migrate to {v.get('migrate_to', 'latest')}",
                    "sunset_date": v["sunset_date"]}
        return {"resolved": requested, "status": v["status"]}

    def latest(self) -> str:
        stable = [v for v in self._versions.values() if v["status"] == "stable"]
        return stable[-1]["version"] if stable else ""

    def summary(self) -> dict:
        by_status: dict[str, int] = {}
        for v in self._versions.values():
            by_status[v["status"]] = by_status.get(v["status"], 0) + 1
        return {"total": len(self._versions), "by_status": by_status,
                "latest": self.latest()}
