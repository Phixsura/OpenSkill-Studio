"""Service warmup controller — manage service warmup and cold start optimization."""
from __future__ import annotations
import time


class WarmupController:
    def __init__(self):
        self._services: dict[str, dict] = {}

    def register(self, name: str, warmup_steps: list[str]) -> dict:
        self._services[name] = {"name": name, "steps": warmup_steps,
                                 "status": "cold", "warmed_at": 0}
        return {"name": name, "steps": len(warmup_steps)}

    def warmup(self, name: str) -> dict:
        svc = self._services[name]
        results = []
        for step in svc["steps"]:
            results.append({"step": step, "status": "completed"})
        svc["status"] = "warm"
        svc["warmed_at"] = time.time()
        return {"name": name, "status": "warm", "steps_completed": len(results)}

    def is_warm(self, name: str) -> bool:
        return self._services.get(name, {}).get("status") == "warm"

    def cold_services(self) -> list[str]:
        return [n for n, s in self._services.items() if s["status"] == "cold"]

    def stats(self) -> dict:
        warm = sum(1 for s in self._services.values() if s["status"] == "warm")
        return {"total": len(self._services), "warm": warm, "cold": len(self._services) - warm}
