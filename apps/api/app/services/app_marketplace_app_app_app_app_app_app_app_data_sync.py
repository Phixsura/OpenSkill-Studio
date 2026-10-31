"""Data sync engine — synchronize data between systems."""
from __future__ import annotations
import time


def create_sync_job(source: str, destination: str, records: int) -> dict:
    return {"source": source, "destination": destination, "total_records": records,
            "synced": 0, "failed": 0, "status": "running", "started_at": time.time()}


def update_progress(job: dict, synced: int, failed: int = 0) -> dict:
    job["synced"] += synced
    job["failed"] += failed
    done = job["synced"] + job["failed"]
    if done >= job["total_records"]:
        job["status"] = "completed" if job["failed"] == 0 else "completed_with_errors"
    pct = round(done / max(job["total_records"], 1) * 100)
    return {"synced": job["synced"], "failed": job["failed"], "progress_pct": pct,
            "status": job["status"]}


def sync_summary(jobs: list[dict]) -> dict:
    total_records = sum(j["total_records"] for j in jobs)
    total_synced = sum(j["synced"] for j in jobs)
    total_failed = sum(j["failed"] for j in jobs)
    running = sum(1 for j in jobs if j["status"] == "running")
    return {"total_jobs": len(jobs), "running": running,
            "total_records": total_records, "total_synced": total_synced,
            "total_failed": total_failed,
            "success_rate": round(total_synced / max(total_records, 1) * 100)}
