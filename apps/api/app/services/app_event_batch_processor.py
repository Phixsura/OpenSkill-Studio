"""Event batch processor — process multiple events efficiently."""

from datetime import UTC, datetime


def create_batch(events: list[dict]) -> dict:
    """Create a batch of events for processing."""
    return {
        "batch_id": f"batch_{int(datetime.now(UTC).timestamp())}",
        "events": events,
        "count": len(events),
        "created_at": datetime.now(UTC).isoformat(),
        "status": "pending",
    }


def split_batch(events: list[dict], *, chunk_size: int = 50) -> list[list[dict]]:
    """Split events into chunks for parallel processing."""
    return [events[i:i + chunk_size] for i in range(0, len(events), chunk_size)]


def merge_batch_results(results: list[dict]) -> dict:
    """Merge results from multiple batch chunks."""
    total = sum(r.get("processed", 0) for r in results)
    failed = sum(r.get("failed", 0) for r in results)
    return {"total_processed": total, "total_failed": failed,
            "success_rate": round((total - failed) / total * 100, 1) if total > 0 else 100.0,
            "chunks": len(results)}
