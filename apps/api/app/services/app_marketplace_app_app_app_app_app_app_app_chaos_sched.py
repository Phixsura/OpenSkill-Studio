"""Chaos experiment scheduler — schedule and manage chaos experiments."""
from __future__ import annotations
import time


class ChaosScheduler:
    def __init__(self):
        self._experiments: dict[str, dict] = {}

    def schedule(self, name: str, target: str, fault_type: str,
                 duration_seconds: int = 60, blast_radius: str = "single") -> dict:
        self._experiments[name] = {
            "name": name, "target": target, "fault_type": fault_type,
            "duration_seconds": duration_seconds, "blast_radius": blast_radius,
            "status": "scheduled", "created_at": time.time()}
        return self._experiments[name]

    def start(self, name: str) -> dict:
        exp = self._experiments[name]
        exp["status"] = "running"
        exp["started_at"] = time.time()
        return {"name": name, "status": "running"}

    def stop(self, name: str) -> dict:
        exp = self._experiments[name]
        exp["status"] = "completed"
        return {"name": name, "status": "completed"}

    def abort(self, name: str) -> dict:
        exp = self._experiments[name]
        exp["status"] = "aborted"
        return {"name": name, "status": "aborted"}

    def list_experiments(self, status: str = "") -> list[dict]:
        exps = list(self._experiments.values())
        if status:
            exps = [e for e in exps if e["status"] == status]
        return exps

    def stats(self) -> dict:
        by_status: dict[str, int] = {}
        for e in self._experiments.values():
            by_status[e["status"]] = by_status.get(e["status"], 0) + 1
        return {"total": len(self._experiments), "by_status": by_status}
