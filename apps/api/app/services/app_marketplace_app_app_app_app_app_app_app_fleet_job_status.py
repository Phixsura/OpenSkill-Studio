"""Fleet job status — track CronJob and Job completion rates."""
from __future__ import annotations
def fleet_job_status(jobs: list[dict]) -> dict:
    succeeded = [j for j in jobs if j.get("status") == "succeeded"]
    failed = [j for j in jobs if j.get("status") == "failed"]
    running = [j for j in jobs if j.get("status") == "running"]
    return {"total": len(jobs), "succeeded": len(succeeded), "failed": len(failed),
            "running": len(running), "success_rate": round(len(succeeded) / max(len(jobs), 1) * 100, 1)}
