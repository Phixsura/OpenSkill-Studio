"""Fleet batch jobs — track batch processing metrics."""
from __future__ import annotations
def fleet_batch_job_metrics(jobs: list[dict]) -> dict:
    completed = [j for j in jobs if j.get("status") == "completed"]
    failed = [j for j in jobs if j.get("status") == "failed"]
    avg_dur = round(sum(j.get("duration_min", 0) for j in completed) / max(len(completed), 1), 1)
    return {"total": len(jobs), "completed": len(completed), "failed": len(failed),
            "avg_duration_min": avg_dur, "reliable": len(failed) == 0}
