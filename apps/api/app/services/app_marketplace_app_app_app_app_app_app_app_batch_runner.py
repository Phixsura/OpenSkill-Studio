"""Batch job runner — schedule and track batch processing jobs."""
from __future__ import annotations
import time
import hashlib


def create_job(name: str, item_count: int, batch_size: int = 100) -> dict:
    job_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:10]
    batches = (item_count + batch_size - 1) // batch_size
    return {"job_id": job_id, "name": name, "item_count": item_count,
            "batch_size": batch_size, "total_batches": batches,
            "completed_batches": 0, "failed_batches": 0, "status": "pending"}


def process_batch(job: dict, success: bool = True) -> dict:
    if job["status"] == "completed":
        return {"processed": False, "error": "already_completed"}
    if success:
        job["completed_batches"] += 1
    else:
        job["failed_batches"] += 1
    done = job["completed_batches"] + job["failed_batches"]
    if done >= job["total_batches"]:
        job["status"] = "completed" if job["failed_batches"] == 0 else "completed_with_errors"
    else:
        job["status"] = "running"
    pct = round(done / job["total_batches"] * 100)
    return {"processed": True, "progress_pct": pct, "status": job["status"]}


def job_summary(jobs: list[dict]) -> dict:
    running = sum(1 for j in jobs if j["status"] == "running")
    completed = sum(1 for j in jobs if j["status"] in ("completed", "completed_with_errors"))
    total_items = sum(j["item_count"] for j in jobs)
    return {"total_jobs": len(jobs), "running": running, "completed": completed,
            "pending": len(jobs) - running - completed, "total_items": total_items}
