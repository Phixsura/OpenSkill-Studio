"""Platform task scheduler — cron-like task scheduling."""
from __future__ import annotations
import time


class TaskScheduler:
    def __init__(self):
        self._tasks: dict[str, dict] = {}
        self._executions: list[dict] = []

    def schedule(self, name: str, interval_seconds: int, handler: str) -> dict:
        self._tasks[name] = {"name": name, "interval": interval_seconds,
                              "handler": handler, "enabled": True,
                              "last_run": 0, "run_count": 0}
        return self._tasks[name]

    def tick(self, now: float | None = None) -> list[dict]:
        now = now or time.time()
        triggered = []
        for task in self._tasks.values():
            if not task["enabled"]:
                continue
            if now - task["last_run"] >= task["interval"]:
                task["last_run"] = now
                task["run_count"] += 1
                execution = {"task": task["name"], "triggered_at": now,
                             "run_number": task["run_count"]}
                self._executions.append(execution)
                triggered.append(execution)
        return triggered

    def enable(self, name: str) -> dict:
        self._tasks[name]["enabled"] = True
        return {"name": name, "enabled": True}

    def disable(self, name: str) -> dict:
        self._tasks[name]["enabled"] = False
        return {"name": name, "enabled": False}

    def stats(self) -> dict:
        enabled = sum(1 for t in self._tasks.values() if t["enabled"])
        return {"total_tasks": len(self._tasks), "enabled": enabled,
                "total_executions": len(self._executions)}
