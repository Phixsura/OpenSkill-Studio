"""Deployment progress tracker — track multi-step deployment progress."""
from __future__ import annotations
import time


class DeployProgressTracker:
    def __init__(self):
        self._deployments: dict[str, dict] = {}

    def start(self, deploy_id: str, steps: list[str]) -> dict:
        self._deployments[deploy_id] = {
            "steps": {s: {"status": "pending", "started": False} for s in steps},
            "current_step": 0, "total_steps": len(steps),
            "status": "in_progress", "started_at": time.time()}
        return {"deploy_id": deploy_id, "total_steps": len(steps)}

    def advance(self, deploy_id: str, step: str, status: str = "completed") -> dict:
        d = self._deployments[deploy_id]
        d["steps"][step] = {"status": status, "started": True}
        completed = sum(1 for s in d["steps"].values() if s["status"] == "completed")
        d["current_step"] = completed
        if completed == d["total_steps"]:
            d["status"] = "completed"
        elif status == "failed":
            d["status"] = "failed"
        pct = round(completed / max(d["total_steps"], 1) * 100)
        return {"deploy_id": deploy_id, "step": step, "status": d["status"],
                "progress_pct": pct, "completed": completed}

    def get(self, deploy_id: str) -> dict:
        return dict(self._deployments.get(deploy_id, {}))
