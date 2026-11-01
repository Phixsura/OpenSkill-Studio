"""Sandbox Batch Executor — execute batched operations in extension sandboxes.

Runs multiple operations in a single batch with transaction semantics,
progress tracking, partial failure handling, and result aggregation.
"""
from __future__ import annotations
import secrets
import time
from dataclasses import dataclass, field
from enum import Enum


class BatchStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    PARTIAL = "partial"
    FAILED = "failed"


@dataclass
class BatchOperation:
    op_id: str
    name: str
    params: dict = field(default_factory=dict)
    status: str = "pending"  # pending, success, failed, skipped
    result: dict | None = None
    error: str = ""
    duration_ms: float = 0.0


@dataclass
class BatchJob:
    batch_id: str
    sandbox_id: str
    operations: list[BatchOperation] = field(default_factory=list)
    status: BatchStatus = BatchStatus.PENDING
    stop_on_error: bool = False
    started_at: float = 0.0
    finished_at: float = 0.0
    total_duration_ms: float = 0.0


class SandboxBatchExecutorService:
    """Executes batched operations with transaction-like semantics."""

    MAX_BATCH_SIZE = 100

    def __init__(self):
        self._batches: dict[str, BatchJob] = {}

    def create_batch(self, sandbox_id: str, operations: list[dict],
                     stop_on_error: bool = False) -> BatchJob | dict:
        if len(operations) > self.MAX_BATCH_SIZE:
            return {"error": f"Batch too large (max {self.MAX_BATCH_SIZE})"}
        if not operations:
            return {"error": "Batch must have at least one operation"}

        batch_id = f"bat_{secrets.token_urlsafe(8)}"
        ops = [BatchOperation(
            op_id=f"op_{secrets.token_urlsafe(6)}",
            name=o["name"], params=o.get("params", {}),
        ) for o in operations]

        batch = BatchJob(
            batch_id=batch_id, sandbox_id=sandbox_id,
            operations=ops, stop_on_error=stop_on_error,
        )
        self._batches[batch_id] = batch
        return batch

    def execute(self, batch_id: str, results: list[dict]) -> BatchJob | dict:
        batch = self._batches.get(batch_id)
        if not batch:
            return {"error": "Batch not found"}
        if batch.status != BatchStatus.PENDING:
            return {"error": "Batch already executed"}

        batch.status = BatchStatus.RUNNING
        batch.started_at = time.time()

        for i, op in enumerate(batch.operations):
            if i < len(results):
                r = results[i]
                op.status = "success" if r.get("success", True) else "failed"
                op.result = r.get("result")
                op.error = r.get("error", "")
                op.duration_ms = r.get("duration_ms", 0)

                if op.status == "failed" and batch.stop_on_error:
                    # Skip remaining
                    for j in range(i + 1, len(batch.operations)):
                        batch.operations[j].status = "skipped"
                    break
            else:
                op.status = "skipped"

        batch.finished_at = time.time()
        batch.total_duration_ms = round((batch.finished_at - batch.started_at) * 1000, 1)

        succeeded = sum(1 for o in batch.operations if o.status == "success")
        failed = sum(1 for o in batch.operations if o.status == "failed")

        if failed == 0:
            batch.status = BatchStatus.COMPLETED
        elif succeeded == 0:
            batch.status = BatchStatus.FAILED
        else:
            batch.status = BatchStatus.PARTIAL

        return batch

    def get_batch(self, batch_id: str) -> BatchJob | None:
        return self._batches.get(batch_id)

    def get_summary(self, batch_id: str) -> dict:
        batch = self._batches.get(batch_id)
        if not batch:
            return {}
        return {
            "status": batch.status.value,
            "total": len(batch.operations),
            "succeeded": sum(1 for o in batch.operations if o.status == "success"),
            "failed": sum(1 for o in batch.operations if o.status == "failed"),
            "skipped": sum(1 for o in batch.operations if o.status == "skipped"),
            "duration_ms": batch.total_duration_ms,
        }
