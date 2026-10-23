"""API sandbox environment — isolated test environments with mock data."""
from __future__ import annotations
import secrets


class ApiSandbox:
    def __init__(self):
        self._sandboxes: dict[str, dict] = {}

    def create(self, *, owner: str, name: str = "default",
               seed_data: bool = True, ttl_hours: int = 24) -> dict:
        sid = f"sbx_{secrets.token_hex(6)}"
        self._sandboxes[sid] = {
            "id": sid, "owner": owner, "name": name,
            "base_url": f"https://sandbox-{sid}.api.openskill.io",
            "api_key": f"sbx_key_{secrets.token_hex(12)}",
            "status": "ready", "seeded": seed_data, "ttl_hours": ttl_hours,
            "request_count": 0,
        }
        return {"id": sid, "base_url": self._sandboxes[sid]["base_url"],
                "api_key": self._sandboxes[sid]["api_key"], "status": "ready"}

    def use(self, sid: str) -> dict:
        s = self._sandboxes.get(sid)
        if not s:
            return {"error": "Sandbox not found"}
        s["request_count"] += 1
        return {"id": sid, "request_count": s["request_count"], "status": s["status"]}

    def destroy(self, sid: str) -> dict:
        if sid not in self._sandboxes:
            return {"error": "Sandbox not found"}
        del self._sandboxes[sid]
        return {"destroyed": True, "id": sid}

    def list_sandboxes(self, owner: str) -> list[dict]:
        return [{"id": s["id"], "name": s["name"], "base_url": s["base_url"],
                 "status": s["status"], "request_count": s["request_count"]}
                for s in self._sandboxes.values() if s["owner"] == owner]
