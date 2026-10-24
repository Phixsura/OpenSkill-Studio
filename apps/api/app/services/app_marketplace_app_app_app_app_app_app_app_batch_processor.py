"""Batch job processor — process items in configurable batches with progress."""
from __future__ import annotations
import math


class BatchProcessor:
    def __init__(self, items: list, *, batch_size: int = 100):
        self._items = items
        self._batch_size = batch_size
        self._processed = 0
        self._failed = 0
        self._results: list[dict] = []

    def total_batches(self) -> int:
        return math.ceil(len(self._items) / max(self._batch_size, 1))

    def process_batch(self, batch_index: int, *, success_rate: float = 1.0) -> dict:
        start = batch_index * self._batch_size
        end = min(start + self._batch_size, len(self._items))
        batch = self._items[start:end]
        succeeded = int(len(batch) * success_rate)
        failed = len(batch) - succeeded
        self._processed += succeeded
        self._failed += failed
        return {"batch": batch_index, "size": len(batch),
                "succeeded": succeeded, "failed": failed,
                "total_processed": self._processed}

    def progress(self) -> dict:
        total = len(self._items)
        done = self._processed + self._failed
        pct = round(done / max(total, 1) * 100, 1)
        return {"total_items": total, "processed": self._processed,
                "failed": self._failed, "remaining": total - done,
                "progress_pct": pct, "progress_display": f"{pct}%",
                "batches_total": self.total_batches(),
                "status": "completed" if done >= total else "in_progress"}
