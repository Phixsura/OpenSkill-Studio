"""App version manager — track and manage app version history."""
from __future__ import annotations


class AppVersionManager:
    def __init__(self):
        self._versions: dict[str, list[dict]] = {}

    def publish(self, app_id: str, *, version: str, changelog: str = "",
                 size_kb: int = 0) -> dict:
        versions = self._versions.setdefault(app_id, [])
        for v in versions:
            v["latest"] = False
        entry = {"version": version, "changelog": changelog,
                 "size_kb": size_kb, "latest": True, "status": "published"}
        versions.append(entry)
        return {"app_id": app_id, "version": version, "status": "published",
                "total_versions": len(versions)}

    def get_latest(self, app_id: str) -> dict | None:
        versions = self._versions.get(app_id, [])
        return next((v for v in reversed(versions) if v["latest"]), None)

    def list_versions(self, app_id: str) -> list[dict]:
        return list(reversed(self._versions.get(app_id, [])))

    def rollback(self, app_id: str, target_version: str) -> dict:
        versions = self._versions.get(app_id, [])
        target = next((v for v in versions if v["version"] == target_version), None)
        if not target:
            return {"error": "Version not found"}
        for v in versions:
            v["latest"] = False
        target["latest"] = True
        return {"app_id": app_id, "rolled_back_to": target_version}
