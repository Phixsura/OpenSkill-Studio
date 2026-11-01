"""Scheduled task runner — manage cron-like scheduled tasks."""
from __future__ import annotations
import time

_tasks: dict[str, dict] = {}


def create_task(name: str, schedule: str, handler: str, enabled: bool = True) -> dict:
    _tasks[name] = {"name": name, "schedule": schedule, "handler": handler,
                     "enabled": enabled, "run_count": 0, "last_run": None,
                     "last_status": None, "created_at": time.time()}
    return _tasks[name]


def run_task(name: str) -> dict:
    t = _tasks.get(name)
    if not t:
        return {"ran": False, "error": "not_found"}
    if not t["enabled"]:
        return {"ran": False, "error": "disabled"}
    t["run_count"] += 1
    t["last_run"] = time.time()
    t["last_status"] = "success"
    return {"ran": True, "name": name, "run_count": t["run_count"]}


def list_tasks() -> list[dict]:
    return sorted(_tasks.values(), key=lambda t: t["name"])


def toggle_task(name: str) -> dict:
    t = _tasks.get(name)
    if not t:
        return {"toggled": False, "error": "not_found"}
    t["enabled"] = not t["enabled"]
    return {"toggled": True, "name": name, "enabled": t["enabled"]}


def clear_tasks() -> None:
    _tasks.clear()
