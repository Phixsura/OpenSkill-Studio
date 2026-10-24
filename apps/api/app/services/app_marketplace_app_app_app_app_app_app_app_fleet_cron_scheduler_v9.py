"""Fleet Cron Scheduler v9 — track scheduled job execution and failures."""
from __future__ import annotations
def fleet_cron_scheduler_v9(jobs: list[dict]) -> dict:
    running = [j for j in jobs if j.get("status") == "running"]
    failed_last = [j for j in jobs if j.get("last_result") == "failed"]
    next_due = sum(1 for j in jobs if j.get("due_in_min", 999) < 5)
    return {"total_jobs": len(jobs), "running": len(running), "failed_last_run": len(failed_last),
            "due_soon": next_due, "healthy": len(failed_last) == 0}
