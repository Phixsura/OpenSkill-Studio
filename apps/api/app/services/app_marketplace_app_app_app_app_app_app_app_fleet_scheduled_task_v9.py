"""Fleet Scheduled Task v9 — track recurring task execution and SLA."""
from __future__ import annotations
def fleet_scheduled_task_v9(tasks: list[dict]) -> dict:
    on_time = [t for t in tasks if t.get("on_time", True)]
    late = [t for t in tasks if not t.get("on_time", True)]
    avg_drift = sum(t.get("drift_sec", 0) for t in tasks) / len(tasks) if tasks else 0
    return {"total": len(tasks), "on_time": len(on_time), "late": len(late),
            "avg_drift_sec": round(avg_drift, 1), "healthy": len(late) == 0}
