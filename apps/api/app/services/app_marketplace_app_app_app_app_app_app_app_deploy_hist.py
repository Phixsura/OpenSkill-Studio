"""Deployment history — track all deployments with metadata."""
from __future__ import annotations

class DeploymentHistory:
    def __init__(self):
        self._deploys: list[dict] = []

    def record(self, version: str, env: str, deployer: str, status: str = "success") -> dict:
        entry = {"version": version, "env": env, "deployer": deployer,
                 "status": status, "seq": len(self._deploys) + 1}
        self._deploys.append(entry)
        return entry

    def recent(self, limit: int = 10, env: str = "") -> list[dict]:
        filtered = self._deploys if not env else [d for d in self._deploys if d["env"] == env]
        return filtered[-limit:]

    def stats(self) -> dict:
        success = sum(1 for d in self._deploys if d["status"] == "success")
        return {"total": len(self._deploys), "success": success,
                "failed": len(self._deploys) - success,
                "success_rate": round(success / max(len(self._deploys), 1) * 100, 1)}
