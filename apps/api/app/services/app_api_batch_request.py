"""App API Batch Request — process multiple API requests in one call.

Manages batch requests:
- Accept multiple operations in one request
- Track individual operation results
- Compute batch-level success/failure
- Per-installation scoped batches
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class BatchOperation:
    """A single operation in a batch."""

    operation_id: str
    method: str
    path: str
    status_code: int | None = None
    error: str = ""

    @property
    def succeeded(self) -> bool | None:
        if self.status_code is None:
            return None
        return 200 <= self.status_code < 400


@dataclass
class BatchRequest:
    """A batch of API operations."""

    batch_id: str
    operations: list[BatchOperation]

    @property
    def total(self) -> int:
        return len(self.operations)

    @property
    def success_count(self) -> int:
        return sum(1 for o in self.operations if o.succeeded is True)

    @property
    def failure_count(self) -> int:
        return sum(1 for o in self.operations if o.succeeded is False)

    @property
    def all_complete(self) -> bool:
        return all(o.status_code is not None for o in self.operations)


class AppAPIBatchRequest:
    """Process multiple API requests in one call."""

    def __init__(self, max_operations: int = 50) -> None:
        self._max_ops = max_operations
        self._batches: dict[tuple[str, str], BatchRequest] = {}

    def create_batch(
        self, installation_id: str, batch_id: str, operations: list[dict],
    ) -> BatchRequest:
        if not installation_id:
            raise ValueError("installation_id is required")
        if len(operations) > self._max_ops:
            raise ValueError(f"Max {self._max_ops} operations per batch")
        if not operations:
            raise ValueError("at least one operation required")

        ops = [BatchOperation(operation_id=o["id"], method=o["method"].upper(), path=o["path"]) for o in operations]
        batch = BatchRequest(batch_id=batch_id, operations=ops)
        self._batches[(installation_id, batch_id)] = batch
        return batch

    def record_result(
        self, installation_id: str, batch_id: str, operation_id: str,
        status_code: int, error: str = "",
    ) -> BatchOperation:
        b = self._get(installation_id, batch_id)
        for op in b.operations:
            if op.operation_id == operation_id:
                op.status_code = status_code
                op.error = error
                return op
        raise KeyError(f"Operation {operation_id} not found")

    def get_batch(self, installation_id: str, batch_id: str) -> BatchRequest:
        return self._get(installation_id, batch_id)

    def _get(self, installation_id: str, batch_id: str) -> BatchRequest:
        key = (installation_id, batch_id)
        b = self._batches.get(key)
        if b is None:
            raise KeyError(f"Batch {batch_id} not found")
        return b
