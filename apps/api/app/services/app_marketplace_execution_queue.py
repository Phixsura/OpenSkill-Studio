"""Execution Queue — manage queued sandbox executions with priorities.

Provides a priority queue for extension sandbox executions with
concurrency control, deadlines, and status tracking.
"""
from __future__ import annotations
import heapq
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    TIMED_OUT = "timed_out"


@dataclass
class ExecutionJob:
    job_id: str
    extension_id: str
    priority: int  # lower = higher priority
    payload: dict
    status: JobStatus = JobStatus.QUEUED
    created_at: str = ""
    started_at: str = ""
    completed_at: str = ""
    result: dict = field(default_factory=dict)
    error: str = ""
    deadline_seconds: float = 300.0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()

    def __lt__(self, other: "ExecutionJob") -> bool:
        return self.priority < other.priority


class ExecutionQueue:
    """Priority queue for sandbox executions with concurrency control."""

    def __init__(self, max_concurrent: int = 10):
        self._queue: list[ExecutionJob] = []
        self._jobs: dict[str, ExecutionJob] = {}
        self._running: set[str] = set()
        self._max_concurrent = max_concurrent

    def enqueue(self, job: ExecutionJob) -> ExecutionJob:
        """Add a job to the priority queue."""
        self._jobs[job.job_id] = job
        heapq.heappush(self._queue, job)
        return job

    def dequeue(self) -> ExecutionJob | None:
        """Get the next job to run, respecting concurrency limits."""
        if len(self._running) >= self._max_concurrent:
            return None
        while self._queue:
            job = heapq.heappop(self._queue)
            if job.status == JobStatus.QUEUED:
                job.status = JobStatus.RUNNING
                job.started_at = datetime.now(timezone.utc).isoformat()
                self._running.add(job.job_id)
                return job
        return None

    def complete(self, job_id: str, result: dict | None = None) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status == JobStatus.RUNNING:
            job.status = JobStatus.COMPLETED
            job.result = result or {}
            job.completed_at = datetime.now(timezone.utc).isoformat()
            self._running.discard(job_id)
            return True
        return False

    def fail(self, job_id: str, error: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status == JobStatus.RUNNING:
            job.status = JobStatus.FAILED
            job.error = error
            job.completed_at = datetime.now(timezone.utc).isoformat()
            self._running.discard(job_id)
            return True
        return False

    def cancel(self, job_id: str) -> bool:
        job = self._jobs.get(job_id)
        if job and job.status in (JobStatus.QUEUED, JobStatus.RUNNING):
            job.status = JobStatus.CANCELED
            self._running.discard(job_id)
            return True
        return False

    def get_job(self, job_id: str) -> ExecutionJob | None:
        return self._jobs.get(job_id)

    def get_queue_depth(self) -> int:
        return sum(1 for j in self._queue if j.status == JobStatus.QUEUED)

    def get_running_count(self) -> int:
        return len(self._running)

    def get_stats(self) -> dict:
        by_status = {s.value: 0 for s in JobStatus}
        for j in self._jobs.values():
            by_status[j.status.value] += 1
        return {
            "total": len(self._jobs),
            "queue_depth": self.get_queue_depth(),
            "running": self.get_running_count(),
            "max_concurrent": self._max_concurrent,
            "by_status": by_status,
        }
