"""Endpoint Batch Processor — batch API request execution with parallel/sequential modes."""
from __future__ import annotations

import structlog
from dataclasses import dataclass, field

logger = structlog.get_logger()


@dataclass
class BatchRequest:
    request_id: str
    endpoint_id: str
    method: str
    body: dict = field(default_factory=dict)


@dataclass
class BatchResult:
    request_id: str
    status_code: int
    body: dict = field(default_factory=dict)
    error: str = ""
    latency_ms: float = 0.0


@dataclass
class BatchJob:
    batch_id: str
    consumer_id: str
    requests: list[BatchRequest]
    mode: str = "parallel"  # parallel, sequential
    status: str = "pending"  # pending, running, completed, failed
    results: list[BatchResult] = field(default_factory=list)
    max_concurrent: int = 10


@dataclass
class BatchProcessor:
    """Execute batch API requests with parallel or sequential modes."""

    _jobs: dict[str, BatchJob] = field(default_factory=dict)
    _max_batch_size: int = 100

    def configure(self, max_batch_size: int = 100) -> dict:
        if max_batch_size < 1:
            raise ValueError("max_batch_size must be positive")
        self._max_batch_size = max_batch_size
        return {"max_batch_size": max_batch_size}

    def create_batch(self, batch_id: str, consumer_id: str,
                     requests: list[BatchRequest],
                     mode: str = "parallel") -> dict:
        if batch_id in self._jobs:
            raise ValueError(f"Batch {batch_id} already exists")
        if len(requests) > self._max_batch_size:
            raise ValueError(f"Batch exceeds max size of {self._max_batch_size}")
        if len(requests) == 0:
            raise ValueError("Batch must have at least one request")
        if mode not in ("parallel", "sequential"):
            raise ValueError(f"Invalid mode: {mode}")
        job = BatchJob(batch_id=batch_id, consumer_id=consumer_id,
                       requests=requests, mode=mode)
        self._jobs[batch_id] = job
        logger.info("batch_created", batch_id=batch_id, size=len(requests))
        return {"batch_id": batch_id, "size": len(requests), "mode": mode}

    def execute(self, batch_id: str, handler=None) -> dict:
        job = self._jobs.get(batch_id)
        if not job:
            raise ValueError(f"Batch {batch_id} not found")
        if job.status == "completed":
            raise ValueError("Batch already completed")
        job.status = "running"
        results = []
        for req in job.requests:
            if handler:
                result = handler(req)
                results.append(result)
            else:
                results.append(BatchResult(
                    request_id=req.request_id,
                    status_code=200,
                    body={"processed": True, "endpoint": req.endpoint_id},
                ))
        job.results = results
        failed = sum(1 for r in results if r.status_code >= 400)
        job.status = "completed" if failed == 0 else "failed"
        logger.info("batch_executed", batch_id=batch_id, total=len(results), failed=failed)
        return {
            "batch_id": batch_id,
            "status": job.status,
            "total": len(results),
            "succeeded": len(results) - failed,
            "failed": failed,
        }

    def get_results(self, batch_id: str) -> dict:
        job = self._jobs.get(batch_id)
        if not job:
            return {"error": "not_found"}
        return {
            "batch_id": batch_id,
            "status": job.status,
            "mode": job.mode,
            "total_requests": len(job.requests),
            "results": [
                {"request_id": r.request_id, "status_code": r.status_code,
                 "error": r.error}
                for r in job.results
            ],
        }

    def get_job(self, batch_id: str) -> dict | None:
        job = self._jobs.get(batch_id)
        if not job:
            return None
        return {
            "batch_id": job.batch_id, "consumer_id": job.consumer_id,
            "mode": job.mode, "status": job.status,
            "request_count": len(job.requests),
            "result_count": len(job.results),
        }

    def list_jobs(self, consumer_id: str | None = None) -> list[dict]:
        jobs = list(self._jobs.values())
        if consumer_id:
            jobs = [j for j in jobs if j.consumer_id == consumer_id]
        return [self.get_job(j.batch_id) for j in jobs]

    def cancel(self, batch_id: str) -> dict:
        job = self._jobs.get(batch_id)
        if not job:
            return {"cancelled": False}
        if job.status in ("completed", "failed"):
            return {"cancelled": False, "reason": "already_finished"}
        job.status = "failed"
        return {"cancelled": True}
