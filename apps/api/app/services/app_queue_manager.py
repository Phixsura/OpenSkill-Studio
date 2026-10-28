"""App Queue Manager — in-memory job queue with priority and dead-letter support.

Manages background job queues for installed apps:
- Enqueue jobs with priority (0 = highest)
- Dequeue in priority order (FIFO within same priority)
- Job status tracking: pending → processing → completed / failed
- Dead-letter queue for failed jobs exceeding max retries
- Per-installation scoped queues
"""

from __future__ import annotations

import heapq
import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class JobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    DEAD_LETTER = "dead_letter"


@dataclass
class Job:
    """A queued job."""

    job_id: str
    installation_id: str
    queue_name: str
    payload: dict
    priority: int = 0
    status: JobStatus = JobStatus.PENDING
    attempt: int = 0
    max_retries: int = 3
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None
    error: str | None = None


@dataclass
class QueueStats:
    """Statistics for a queue."""

    queue_name: str
    pending: int
    processing: int
    completed: int
    failed: int
    dead_letter: int


class AppQueueManager:
    """In-memory job queue with priority and dead-letter support."""

    def __init__(self) -> None:
        # (installation_id, queue_name) → priority heap of (priority, created_at, job_id)
        self._heaps: dict[tuple[str, str], list[tuple[int, float, str]]] = {}
        # (installation_id, job_id) → Job
        self._jobs: dict[tuple[str, str], Job] = {}
        # Dead letter storage
        self._dead_letters: dict[tuple[str, str], list[Job]] = {}

    def enqueue(
        self,
        installation_id: str,
        job_id: str,
        queue_name: str,
        payload: dict,
        priority: int = 0,
        max_retries: int = 3,
        now: float | None = None,
    ) -> Job:
        """Add a job to the queue."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not job_id:
            raise ValueError("job_id is required")
        if not queue_name:
            raise ValueError("queue_name is required")
        if priority < 0:
            raise ValueError("priority must be >= 0")

        job_key = (installation_id, job_id)
        if job_key in self._jobs:
            raise ValueError(f"Job {job_id} already exists")

        now = now or time.time()
        job = Job(
            job_id=job_id,
            installation_id=installation_id,
            queue_name=queue_name,
            payload=payload,
            priority=priority,
            max_retries=max_retries,
            created_at=now,
        )
        self._jobs[job_key] = job

        heap_key = (installation_id, queue_name)
        self._heaps.setdefault(heap_key, [])
        heapq.heappush(self._heaps[heap_key], (priority, now, job_id))

        return job

    def dequeue(self, installation_id: str, queue_name: str) -> Job | None:
        """Dequeue the highest-priority pending job."""
        heap_key = (installation_id, queue_name)
        heap = self._heaps.get(heap_key, [])

        while heap:
            _, _, job_id = heapq.heappop(heap)
            job_key = (installation_id, job_id)
            job = self._jobs.get(job_key)
            if job and job.status == JobStatus.PENDING:
                job.status = JobStatus.PROCESSING
                job.started_at = time.time()
                job.attempt += 1
                return job

        return None

    def complete_job(self, installation_id: str, job_id: str) -> Job:
        """Mark a job as completed."""
        job = self._get_job(installation_id, job_id)
        if job.status != JobStatus.PROCESSING:
            raise ValueError(f"Cannot complete job in {job.status} state")
        job.status = JobStatus.COMPLETED
        job.completed_at = time.time()
        return job

    def fail_job(self, installation_id: str, job_id: str,
                 error: str = "", now: float | None = None) -> Job:
        """Mark a job as failed. Re-enqueues if retries remain."""
        job = self._get_job(installation_id, job_id)
        if job.status != JobStatus.PROCESSING:
            raise ValueError(f"Cannot fail job in {job.status} state")

        job.error = error
        now = now or time.time()

        if job.attempt >= job.max_retries:
            job.status = JobStatus.DEAD_LETTER
            dl_key = (installation_id, job.queue_name)
            self._dead_letters.setdefault(dl_key, []).append(job)
            log.warning("job.dead_letter", job_id=job_id, attempts=job.attempt)
        else:
            job.status = JobStatus.PENDING
            heap_key = (installation_id, job.queue_name)
            self._heaps.setdefault(heap_key, [])
            heapq.heappush(self._heaps[heap_key], (job.priority, now, job_id))

        return job

    def get_job(self, installation_id: str, job_id: str) -> Job:
        return self._get_job(installation_id, job_id)

    def get_queue_stats(self, installation_id: str, queue_name: str) -> QueueStats:
        """Get stats for a queue."""
        counts = {s: 0 for s in JobStatus}
        for (inst, _), job in self._jobs.items():
            if inst == installation_id and job.queue_name == queue_name:
                counts[job.status] += 1
        return QueueStats(
            queue_name=queue_name,
            pending=counts[JobStatus.PENDING],
            processing=counts[JobStatus.PROCESSING],
            completed=counts[JobStatus.COMPLETED],
            failed=counts[JobStatus.FAILED],
            dead_letter=counts[JobStatus.DEAD_LETTER],
        )

    def get_dead_letters(self, installation_id: str, queue_name: str) -> list[Job]:
        return list(self._dead_letters.get((installation_id, queue_name), []))

    def queue_size(self, installation_id: str, queue_name: str) -> int:
        """Count pending jobs in a queue."""
        return sum(
            1 for (inst, _), job in self._jobs.items()
            if inst == installation_id and job.queue_name == queue_name
            and job.status == JobStatus.PENDING
        )

    def _get_job(self, installation_id: str, job_id: str) -> Job:
        job_key = (installation_id, job_id)
        job = self._jobs.get(job_key)
        if job is None:
            raise KeyError(f"Job {job_id} not found")
        return job
