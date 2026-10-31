"""App Batch Processor — process items in configurable batches.

Manages batch job processing for installed apps:
- Submit items for batch processing
- Configurable batch size and concurrency
- Track batch status: queued → processing → completed / failed
- Progress tracking with item-level results
- Per-installation scoped batches
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class BatchStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIALLY_FAILED = "partially_failed"


class ItemResult(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class BatchItem:
    """An item in a batch."""

    item_id: str
    payload: dict
    result: ItemResult = ItemResult.PENDING
    error: str = ""


@dataclass
class Batch:
    """A batch of items to process."""

    batch_id: str
    installation_id: str
    items: list[BatchItem]
    status: BatchStatus = BatchStatus.QUEUED
    batch_size: int = 50
    created_at: float = field(default_factory=time.time)
    started_at: float | None = None
    completed_at: float | None = None

    @property
    def total(self) -> int:
        return len(self.items)

    @property
    def processed(self) -> int:
        return sum(1 for i in self.items if i.result != ItemResult.PENDING)

    @property
    def succeeded(self) -> int:
        return sum(1 for i in self.items if i.result == ItemResult.SUCCESS)

    @property
    def failed_count(self) -> int:
        return sum(1 for i in self.items if i.result == ItemResult.FAILED)

    @property
    def progress_pct(self) -> float:
        return (self.processed / self.total * 100) if self.total > 0 else 0.0


class AppBatchProcessor:
    """Process items in configurable batches."""

    def __init__(self) -> None:
        self._batches: dict[tuple[str, str], Batch] = {}

    def create_batch(
        self,
        installation_id: str,
        batch_id: str,
        items: list[dict],
        batch_size: int = 50,
    ) -> Batch:
        """Create a new batch from item payloads."""
        if not installation_id:
            raise ValueError("installation_id is required")
        if not batch_id:
            raise ValueError("batch_id is required")
        if not items:
            raise ValueError("at least one item is required")
        if batch_size < 1:
            raise ValueError("batch_size must be >= 1")

        key = (installation_id, batch_id)
        if key in self._batches:
            raise ValueError(f"Batch {batch_id} already exists")

        batch_items = [
            BatchItem(item_id=f"{batch_id}-{i}", payload=payload)
            for i, payload in enumerate(items)
        ]
        batch = Batch(
            batch_id=batch_id,
            installation_id=installation_id,
            items=batch_items,
            batch_size=batch_size,
        )
        self._batches[key] = batch
        return batch

    def start_batch(self, installation_id: str, batch_id: str) -> Batch:
        """Mark batch as processing."""
        batch = self._get(installation_id, batch_id)
        if batch.status != BatchStatus.QUEUED:
            raise ValueError(f"Cannot start batch in {batch.status} state")
        batch.status = BatchStatus.PROCESSING
        batch.started_at = time.time()
        return batch

    def record_item_result(
        self,
        installation_id: str,
        batch_id: str,
        item_id: str,
        result: ItemResult,
        error: str = "",
    ) -> BatchItem:
        """Record the result for a single item."""
        batch = self._get(installation_id, batch_id)
        for item in batch.items:
            if item.item_id == item_id:
                item.result = result
                item.error = error
                return item
        raise KeyError(f"Item {item_id} not found in batch {batch_id}")

    def complete_batch(self, installation_id: str, batch_id: str) -> Batch:
        """Mark batch as completed (or partially failed)."""
        batch = self._get(installation_id, batch_id)
        if batch.status != BatchStatus.PROCESSING:
            raise ValueError(f"Cannot complete batch in {batch.status} state")

        batch.completed_at = time.time()
        if batch.failed_count == batch.total:
            batch.status = BatchStatus.FAILED
        elif batch.failed_count > 0:
            batch.status = BatchStatus.PARTIALLY_FAILED
        else:
            batch.status = BatchStatus.COMPLETED
        return batch

    def get_batch(self, installation_id: str, batch_id: str) -> Batch:
        return self._get(installation_id, batch_id)

    def get_progress(self, installation_id: str, batch_id: str) -> dict:
        batch = self._get(installation_id, batch_id)
        return {
            "total": batch.total,
            "processed": batch.processed,
            "succeeded": batch.succeeded,
            "failed": batch.failed_count,
            "progress_pct": round(batch.progress_pct, 1),
            "status": batch.status.value,
        }

    def list_batches(self, installation_id: str) -> list[Batch]:
        return [
            b for (inst, _), b in self._batches.items()
            if inst == installation_id
        ]

    def _get(self, installation_id: str, batch_id: str) -> Batch:
        key = (installation_id, batch_id)
        batch = self._batches.get(key)
        if batch is None:
            raise KeyError(f"Batch {batch_id} not found")
        return batch
