"""Scheduled task executor — execute tasks on cron-like schedules."""
from __future__ import annotations


class ScheduledTaskExecutor:
    def __init__(self):
        self._tasks: dict[str, dict] = {}
        self._history: list[dict] = []

    def register(self, name: str, schedule: str, handler: callable | None = None) -> dict:
        self._tasks[name] = {"name": name, "schedule": schedule,
                              "handler": handler, "enabled": True, "runs": 0}
        return {"name": name, "schedule": schedule}

    def execute(self, name: str) -> dict:
        task = self._tasks[name]
        if not task["enabled"]:
            return {"name": name, "executed": False, "reason": "disabled"}
        task["runs"] += 1
        try:
            output = task["handler"]() if task["handler"] else {"ok": True}
            self._history.append({"name": name, "status": "success", "run": task["runs"]})
            return {"name": name, "executed": True, "status": "success", "output": output}
        except Exception as e:
            self._history.append({"name": name, "status": "failed", "error": str(e)})
            return {"name": name, "executed": True, "status": "failed", "error": str(e)}

    def disable(self, name: str) -> dict:
        self._tasks[name]["enabled"] = False
        return {"name": name, "enabled": False}

    def stats(self) -> dict:
        enabled = sum(1 for t in self._tasks.values() if t["enabled"])
        return {"total_tasks": len(self._tasks), "enabled": enabled,
                "total_runs": sum(t["runs"] for t in self._tasks.values())}
