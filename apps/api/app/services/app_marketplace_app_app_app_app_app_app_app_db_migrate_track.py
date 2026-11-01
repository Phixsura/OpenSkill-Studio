"""Database migration tracker — track migration history and status."""
from __future__ import annotations


class MigrationTracker:
    def __init__(self):
        self._migrations: list[dict] = []
        self._applied: set[str] = set()

    def register(self, version: str, description: str, reversible: bool = True) -> dict:
        self._migrations.append({"version": version, "description": description,
                                  "reversible": reversible, "applied": False})
        return {"version": version, "registered": True}

    def apply(self, version: str) -> dict:
        for m in self._migrations:
            if m["version"] == version:
                m["applied"] = True
                self._applied.add(version)
                return {"version": version, "applied": True}
        return {"version": version, "applied": False, "error": "not_found"}

    def pending(self) -> list[dict]:
        return [m for m in self._migrations if not m["applied"]]

    def rollback(self, version: str) -> dict:
        for m in self._migrations:
            if m["version"] == version:
                if not m["reversible"]:
                    return {"version": version, "rolled_back": False, "reason": "irreversible"}
                m["applied"] = False
                self._applied.discard(version)
                return {"version": version, "rolled_back": True}
        return {"version": version, "rolled_back": False, "reason": "not_found"}

    def status(self) -> dict:
        return {"total": len(self._migrations), "applied": len(self._applied),
                "pending": len(self._migrations) - len(self._applied)}
