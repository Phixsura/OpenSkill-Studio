"""Batch Processor — process large datasets in configurable chunks.

Implements:
- Chunk-based processing (split large input into manageable pieces)
- Per-chunk error handling (continue on failure)
- Progress tracking with ETA estimation
- Configurable chunk size
- Result aggregation across chunks
- Resumable processing (track last successful chunk)
"""
from __future__ import annotations
from dataclasses import dataclass, field
import time
import math


@dataclass
class ChunkResult:
    chunk_index: int
    success: bool
    processed: int
    errors: int
    result: object = None
    error_message: str = ""
    duration_ms: float = 0


@dataclass
class BatchResult:
    total_items: int
    total_chunks: int
    chunks_completed: int
    chunks_failed: int
    total_processed: int
    total_errors: int
    duration_ms: float
    results: list[ChunkResult] = field(default_factory=list)
    resumable_from: int = 0

    @property
    def success_rate(self) -> float:
        total = self.total_processed + self.total_errors
        return round(self.total_processed / max(1, total) * 100, 1)


class BatchProcessorService:
    def __init__(self):
        self._progress: dict[str, dict] = {}

    def process(self, items: list, processor: callable,
                chunk_size: int = 100, batch_id: str = "",
                on_progress: callable | None = None,
                resume_from: int = 0) -> BatchResult:
        """Process items in chunks.
        processor(chunk: list) -> result or raises"""
        total = len(items)
        total_chunks = math.ceil(total / chunk_size)
        start = time.time()

        result = BatchResult(total_items=total, total_chunks=total_chunks,
                             chunks_completed=0, chunks_failed=0,
                             total_processed=0, total_errors=0, duration_ms=0)

        for i in range(resume_from, total_chunks):
            chunk_start = time.time()
            chunk = items[i * chunk_size:(i + 1) * chunk_size]

            try:
                chunk_result = processor(chunk)
                cr = ChunkResult(chunk_index=i, success=True,
                                 processed=len(chunk), errors=0,
                                 result=chunk_result,
                                 duration_ms=round((time.time() - chunk_start) * 1000, 2))
                result.chunks_completed += 1
                result.total_processed += len(chunk)
                result.resumable_from = i + 1
            except Exception as e:
                cr = ChunkResult(chunk_index=i, success=False,
                                 processed=0, errors=len(chunk),
                                 error_message=str(e),
                                 duration_ms=round((time.time() - chunk_start) * 1000, 2))
                result.chunks_failed += 1
                result.total_errors += len(chunk)

            result.results.append(cr)

            # Progress callback
            if on_progress:
                progress = {
                    "batch_id": batch_id,
                    "chunk": i + 1, "total_chunks": total_chunks,
                    "pct": round((i + 1) / total_chunks * 100, 1),
                    "processed": result.total_processed,
                    "errors": result.total_errors,
                }
                # ETA
                elapsed = time.time() - start
                if i > resume_from:
                    rate = (i - resume_from + 1) / elapsed
                    remaining = (total_chunks - i - 1) / max(0.001, rate)
                    progress["eta_seconds"] = round(remaining, 1)
                on_progress(progress)

            if batch_id:
                self._progress[batch_id] = {
                    "pct": round((i + 1) / total_chunks * 100, 1),
                    "processed": result.total_processed,
                }

        result.duration_ms = round((time.time() - start) * 1000, 2)
        return result

    def get_progress(self, batch_id: str) -> dict:
        return self._progress.get(batch_id, {})

    @staticmethod
    def chunk_list(items: list, size: int) -> list[list]:
        """Utility: split a list into chunks."""
        return [items[i:i + size] for i in range(0, len(items), size)]
