"""Queue monitor — track message queue health and throughput."""
from __future__ import annotations


def create_queue_stats(name: str, pending: int, processing: int, completed: int,
                       failed: int, avg_latency_ms: float = 0) -> dict:
    total = pending + processing + completed + failed
    throughput = round(completed / max(total, 1) * 100, 1)
    error_rate = round(failed / max(total, 1) * 100, 1)
    health = "healthy" if pending < 1000 and error_rate < 5 else "degraded" if error_rate < 10 else "critical"
    return {"name": name, "pending": pending, "processing": processing,
            "completed": completed, "failed": failed, "total": total,
            "throughput_pct": throughput, "error_rate": error_rate,
            "avg_latency_ms": avg_latency_ms, "health": health}


def aggregate_queues(queues: list[dict]) -> dict:
    total_pending = sum(q["pending"] for q in queues)
    total_failed = sum(q["failed"] for q in queues)
    total_completed = sum(q["completed"] for q in queues)
    unhealthy = [q["name"] for q in queues if q["health"] != "healthy"]
    return {"queue_count": len(queues), "total_pending": total_pending,
            "total_completed": total_completed, "total_failed": total_failed,
            "unhealthy_queues": unhealthy, "all_healthy": len(unhealthy) == 0}
