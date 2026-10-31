"""App install tracker — track installations, uninstalls, and active installs."""
from __future__ import annotations
import time


class InstallTracker:
    def __init__(self):
        self._installs: dict[str, dict] = {}

    def install(self, *, app_id: str, org_id: str, user_id: str,
                 now: float | None = None) -> dict:
        key = f"{app_id}:{org_id}"
        ts = now if now is not None else time.time()
        self._installs[key] = {"app_id": app_id, "org_id": org_id,
                                "installed_by": user_id, "installed_at": ts,
                                "active": True}
        return {"installed": True, "app_id": app_id, "org_id": org_id}

    def uninstall(self, *, app_id: str, org_id: str) -> dict:
        key = f"{app_id}:{org_id}"
        inst = self._installs.get(key)
        if not inst:
            return {"error": "Not installed"}
        inst["active"] = False
        return {"uninstalled": True, "app_id": app_id}

    def is_installed(self, *, app_id: str, org_id: str) -> bool:
        key = f"{app_id}:{org_id}"
        inst = self._installs.get(key)
        return inst is not None and inst["active"]

    def app_stats(self, app_id: str) -> dict:
        installs = [v for v in self._installs.values() if v["app_id"] == app_id]
        active = sum(1 for i in installs if i["active"])
        return {"app_id": app_id, "total_installs": len(installs),
                "active_installs": active, "uninstalls": len(installs) - active}

    def org_apps(self, org_id: str) -> list[str]:
        return [v["app_id"] for v in self._installs.values()
                if v["org_id"] == org_id and v["active"]]
