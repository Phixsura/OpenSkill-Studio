"""Deployment rollout tracker — track progressive rollout status."""
from __future__ import annotations


class RolloutTracker:
    def __init__(self):
        self._rollouts: dict[str, dict] = {}

    def start(self, name: str, target_pct: int = 100, step_pct: int = 10) -> dict:
        self._rollouts[name] = {"name": name, "current_pct": 0,
                                 "target_pct": target_pct, "step_pct": step_pct,
                                 "status": "in_progress", "steps_completed": 0}
        return self._rollouts[name]

    def advance(self, name: str) -> dict:
        r = self._rollouts[name]
        if r["status"] != "in_progress":
            return {"name": name, "advanced": False, "reason": r["status"]}
        r["current_pct"] = min(r["current_pct"] + r["step_pct"], r["target_pct"])
        r["steps_completed"] += 1
        if r["current_pct"] >= r["target_pct"]:
            r["status"] = "completed"
        return {"name": name, "current_pct": r["current_pct"],
                "status": r["status"], "advanced": True}

    def pause(self, name: str) -> dict:
        self._rollouts[name]["status"] = "paused"
        return {"name": name, "status": "paused"}

    def rollback(self, name: str) -> dict:
        self._rollouts[name]["status"] = "rolled_back"
        self._rollouts[name]["current_pct"] = 0
        return {"name": name, "status": "rolled_back"}

    def status(self, name: str) -> dict:
        return dict(self._rollouts[name])

    def list_active(self) -> list[dict]:
        return [r for r in self._rollouts.values() if r["status"] == "in_progress"]
