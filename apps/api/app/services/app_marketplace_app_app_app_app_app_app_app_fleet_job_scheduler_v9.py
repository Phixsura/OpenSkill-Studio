"""Fleet Job Scheduler v9 — track batch job scheduling and completion."""
from __future__ import annotations
def fleet_job_scheduler_v9(jobs: list[dict]) -> dict:
    completed = [j for j in jobs if j.get("status") == "completed"]
    running = [j for j in jobs if j.get("status") == "running"]
    failed = [j for j in jobs if j.get("status") == "failed"]
    avg_runtime = sum(j.get("runtime_min", 0) for j in completed) / len(completed) if completed else 0
    return {"total": len(jobs), "completed": len(completed), "running": len(running),
            "failed": len(failed), "avg_runtime_min": round(avg_runtime, 1), "healthy": len(failed) == 0}
