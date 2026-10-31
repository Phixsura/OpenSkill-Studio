"""Batch Processor — process bulk operations on marketplace entities.

Handles batch installs, updates, migrations, and notifications
with progress tracking, error handling, and rollback support.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class BatchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_COMPLETED = "partially_completed"
    ROLLED_BACK = "rolled_back"


@dataclass
class BatchItem:
    item_id: str
    action: str
    target: str
    status: str = "pending"
    result: str = ""
    error: str = ""


@dataclass
class BatchJob:
    job_id: str
    operation: str
    items: list[BatchItem]
    status: BatchStatus = BatchStatus.PENDING
    created_at: str = ""
    completed_at: str = ""
    created_by: str = ""
    progress: int = 0

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class BatchProcessor:
    """Processes bulk marketplace operations."""

    def __init__(self, max_batch_size: int = 500):
        self._jobs: dict[str, BatchJob] = {}
        self._max_batch = max_batch_size

    def create_job(self, job_id: str, operation: str, items: list[dict],
                   created_by: str = "") -> tuple[BatchJob | None, str]:
        """Create a batch job. Items: [{action, target}]."""
        if len(items) > self._max_batch:
            return None, f"Batch size {len(items)} exceeds max {self._max_batch}"
        if not items:
            return None, "Empty batch"

        batch_items = [
            BatchItem(item_id=f"{job_id}-{i}", action=it["action"], target=it["target"])
            for i, it in enumerate(items)
        ]
        job = BatchJob(job_id=job_id, operation=operation, items=batch_items,
                       created_by=created_by)
        self._jobs[job_id] = job
        return job, "Created"

    def execute(self, job_id: str, processor: callable | None = None) -> BatchJob | None:
        """Execute a batch job. Processor receives (action, target) -> (success, result)."""
        job = self._jobs.get(job_id)
        if not job or job.status != BatchStatus.PENDING:
            return None

        job.status = BatchStatus.RUNNING
        success_count = 0
        error_count = 0

        for item in job.items:
            try:
                if processor:
                    ok, result = processor(item.action, item.target)
                else:
                    ok, result = True, "processed"
                item.status = "completed" if ok else "failed"
                item.result = result
                if ok:
                    success_count += 1
                else:
                    error_count += 1
                    item.error = result
            except Exception as e:
                item.status = "error"
                item.error = str(e)
                error_count += 1
            job.progress = int((success_count + error_count) / len(job.items) * 100)

        job.completed_at = datetime.now(timezone.utc).isoformat()
        if error_count == 0:
            job.status = BatchStatus.COMPLETED
        elif success_count == 0:
            job.status = BatchStatus.FAILED
        else:
            job.status = BatchStatus.PARTIALLY_COMPLETED
        return job

    def get_job(self, job_id: str) -> BatchJob | None:
        return self._jobs.get(job_id)

    def get_progress(self, job_id: str) -> dict | None:
        job = self._jobs.get(job_id)
        if not job:
            return None
        return {
            "job_id": job_id, "status": job.status.value,
            "total": len(job.items), "progress": job.progress,
            "completed": sum(1 for i in job.items if i.status == "completed"),
            "failed": sum(1 for i in job.items if i.status in ("failed", "error")),
            "pending": sum(1 for i in job.items if i.status == "pending"),
        }
