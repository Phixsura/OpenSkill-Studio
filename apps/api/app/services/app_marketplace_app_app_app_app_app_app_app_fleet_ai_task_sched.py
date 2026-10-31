"""Fleet AI Task Scheduler — track cron and periodic AI task execution."""
from __future__ import annotations
def fleet_ai_task_scheduler(schedulers: list[dict]) -> dict:
    active = [s for s in schedulers if s.get("active", True)]
    tasks = sum(s.get("tasks", 0) for s in schedulers)
    executions_24h = sum(s.get("executions_24h", 0) for s in schedulers)
    failures_24h = sum(s.get("failures_24h", 0) for s in schedulers)
    return {"schedulers": len(schedulers), "active": len(active), "tasks": tasks,
            "executions_24h": executions_24h, "failures_24h": failures_24h, "reliable": failures_24h == 0}
