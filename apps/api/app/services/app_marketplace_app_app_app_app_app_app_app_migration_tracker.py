"""Database migration tracker — track schema versions and migration history."""
from __future__ import annotations


class MigrationTracker:
    def __init__(self):
        self._migrations: list[dict] = []
        self._current_version: str = "0.0.0"

    def register(self, *, version: str, description: str, sql_up: str, sql_down: str) -> dict:
        m = {"version": version, "description": description,
             "sql_up": sql_up, "sql_down": sql_down,
             "applied": False, "index": len(self._migrations)}
        self._migrations.append(m)
        return {"registered": version, "index": m["index"]}

    def apply(self, version: str) -> dict:
        m = next((m for m in self._migrations if m["version"] == version), None)
        if not m:
            return {"error": f"Migration {version} not found"}
        if m["applied"]:
            return {"error": f"Migration {version} already applied"}
        m["applied"] = True
        self._current_version = version
        return {"applied": version, "description": m["description"],
                "current_version": self._current_version}

    def rollback(self, version: str) -> dict:
        m = next((m for m in self._migrations if m["version"] == version), None)
        if not m:
            return {"error": f"Migration {version} not found"}
        if not m["applied"]:
            return {"error": f"Migration {version} not applied"}
        m["applied"] = False
        applied = [mg for mg in self._migrations if mg["applied"]]
        self._current_version = applied[-1]["version"] if applied else "0.0.0"
        return {"rolled_back": version, "current_version": self._current_version}

    def status(self) -> dict:
        applied = [m for m in self._migrations if m["applied"]]
        pending = [m for m in self._migrations if not m["applied"]]
        return {"current_version": self._current_version,
                "total": len(self._migrations),
                "applied": len(applied), "pending": len(pending),
                "pending_list": [{"version": m["version"], "description": m["description"]} for m in pending]}
