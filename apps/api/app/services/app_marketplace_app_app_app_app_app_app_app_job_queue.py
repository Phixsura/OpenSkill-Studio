"""Job queue processor — priority-based job queue with retries."""
from __future__ import annotations
import time


class JobQueue:
    def __init__(self, max_retries: int = 3):
        self._queue: list[dict] = []
        self._completed: list[dict] = []
        self._failed: list[dict] = []
        self._max_retries = max_retries

    def enqueue(self, job_id: str, payload: dict, priority: int = 0) -> dict:
        job = {"id": job_id, "payload": payload, "priority": priority,
               "attempts": 0, "status": "pending", "created_at": time.time()}
        self._queue.append(job)
        self._queue.sort(key=lambda j: -j["priority"])
        return {"id": job_id, "position": self._queue.index(job) + 1}

    def dequeue(self) -> dict | None:
        if not self._queue:
            return None
        job = self._queue.pop(0)
        job["attempts"] += 1
        job["status"] = "processing"
        return job

    def complete(self, job: dict) -> dict:
        job["status"] = "completed"
        self._completed.append(job)
        return {"id": job["id"], "status": "completed"}

    def fail(self, job: dict, error: str) -> dict:
        if job["attempts"] < self._max_retries:
            job["status"] = "pending"
            job["last_error"] = error
            self._queue.append(job)
            return {"id": job["id"], "status": "retrying", "attempt": job["attempts"]}
        job["status"] = "failed"
        job["last_error"] = error
        self._failed.append(job)
        return {"id": job["id"], "status": "failed", "attempts": job["attempts"]}

    def stats(self) -> dict:
        return {"pending": len(self._queue), "completed": len(self._completed),
                "failed": len(self._failed),
                "total": len(self._queue) + len(self._completed) + len(self._failed)}
