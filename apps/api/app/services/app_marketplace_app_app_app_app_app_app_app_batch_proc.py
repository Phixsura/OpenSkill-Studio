"""Batch job processor — process large data sets in configurable batches."""
from __future__ import annotations
import time


def process_batch(items: list, batch_size: int, processor: callable) -> dict:
    results = []
    failed = 0
    start = time.monotonic()
    for i in range(0, len(items), batch_size):
        batch = items[i:i + batch_size]
        batch_num = i // batch_size + 1
        try:
            output = processor(batch)
            results.append({"batch": batch_num, "size": len(batch), "status": "success", "output": output})
        except Exception as e:
            failed += 1
            results.append({"batch": batch_num, "size": len(batch), "status": "failed", "error": str(e)})
    elapsed = round((time.monotonic() - start) * 1000, 1)
    return {"total_items": len(items), "batch_size": batch_size,
            "total_batches": len(results), "failed_batches": failed,
            "elapsed_ms": elapsed, "batches": results}


def estimate_time(total_items: int, batch_size: int, avg_batch_ms: float) -> dict:
    num_batches = (total_items + batch_size - 1) // batch_size
    total_ms = num_batches * avg_batch_ms
    return {"num_batches": num_batches, "estimated_ms": round(total_ms, 1),
            "estimated_minutes": round(total_ms / 60000, 2)}
