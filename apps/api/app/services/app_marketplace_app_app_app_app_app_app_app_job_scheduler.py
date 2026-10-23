"""Background job scheduler — enqueue, track, and retry async jobs."""
from __future__ import annotations
import secrets
import time


class JobScheduler:
    def __init__(self):
        self._jobs: dict[str, dict] = {}
        self._queues: dict[str, list[str]] = {}

    def enqueue(self, *, queue: str = "default", job_type: str, payload: dict,
                max_retries: int = 3, priority: int = 0) -> dict:
        job_id = f"job_{secrets.token_hex(8)}"
        self._jobs[job_id] = {
            "id": job_id, "queue": queue, "type": job_type,
            "payload": payload, "status": "pending",
            "retries": 0, "max_retries": max_retries,
            "priority": priority, "created": time.time(),
        }
        self._queues.setdefault(queue, []).append(job_id)
        return {"job_id": job_id, "queue": queue, "status": "pending"}

    def process(self, job_id: str, *, success: bool = True, error: str = "") -> dict:
        job = self._jobs.get(job_id)
        if not job:
            return {"error": "Job not found"}
        if success:
            job["status"] = "completed"
            return {"job_id": job_id, "status": "completed"}
        job["retries"] += 1
        if job["retries"] >= job["max_retries"]:
            job["status"] = "failed"
            return {"job_id": job_id, "status": "failed", "retries": job["retries"], "error": error}
        job["status"] = "retrying"
        return {"job_id": job_id, "status": "retrying", "retry": job["retries"]}

    def stats(self, queue: str = "default") -> dict:
        jobs = [self._jobs[jid] for jid in self._queues.get(queue, []) if jid in self._jobs]
        by_status: dict[str, int] = {}
        for j in jobs:
            by_status[j["status"]] = by_status.get(j["status"], 0) + 1
        return {"queue": queue, "total": len(jobs), "by_status": by_status}
