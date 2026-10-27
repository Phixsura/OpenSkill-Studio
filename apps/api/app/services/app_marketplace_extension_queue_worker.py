"""Extension Queue Worker — background job processing for extensions."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
import time


@dataclass
class QueueJob:
    job_id: str
    extension_id: str
    queue: str
    payload: dict
    status: str = "pending"  # pending, processing, completed, failed, dead
    attempts: int = 0
    max_attempts: int = 3
    created_at: float = 0.0
    started_at: float = 0.0
    completed_at: float = 0.0
    error: str = ""
    def __post_init__(self):
        if not self.created_at: self.created_at = time.time()


class ExtQueueWorkerService:
    def __init__(self):
        self._queues: dict[str, deque[QueueJob]] = {}
        self._jobs: dict[str, QueueJob] = {}
        self._counter = 0

    def enqueue(self, extension_id: str, queue: str, payload: dict,
                max_attempts: int = 3) -> QueueJob:
        self._counter += 1
        job = QueueJob(job_id=f"job-{self._counter}", extension_id=extension_id,
                       queue=queue, payload=payload, max_attempts=max_attempts)
        if queue not in self._queues:
            self._queues[queue] = deque()
        self._queues[queue].append(job)
        self._jobs[job.job_id] = job
        return job

    def dequeue(self, queue: str) -> QueueJob | None:
        q = self._queues.get(queue)
        if not q: return None
        while q:
            job = q.popleft()
            if job.status == "pending":
                job.status = "processing"
                job.started_at = time.time()
                job.attempts += 1
                return job
        return None

    def complete(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != "processing": return False
        job.status = "completed"
        job.completed_at = time.time()
        return True

    def fail(self, job_id: str, error: str = "") -> bool:
        job = self._jobs.get(job_id)
        if not job or job.status != "processing": return False
        job.error = error
        if job.attempts >= job.max_attempts:
            job.status = "dead"
        else:
            job.status = "pending"
            q = self._queues.get(job.queue)
            if q is not None:
                q.append(job)
        return True

    def get_stats(self, queue: str) -> dict:
        jobs = [j for j in self._jobs.values() if j.queue == queue]
        return {s: sum(1 for j in jobs if j.status == s)
                for s in ["pending", "processing", "completed", "failed", "dead"]}
