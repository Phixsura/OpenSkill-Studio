"""Queue monitor — monitor background job queues."""


def get_queue_status(*, queues: list[dict]) -> dict:
    results = []
    for q in queues:
        pending = q.get("pending", 0)
        processing = q.get("processing", 0)
        failed = q.get("failed", 0)
        completed = q.get("completed", 0)
        total = pending + processing + failed + completed
        throughput = q.get("throughput_per_min", 0)
        eta_min = round(pending / max(throughput, 0.1), 1) if pending > 0 else 0
        results.append({
            "name": q["name"],
            "pending": pending, "processing": processing,
            "failed": failed, "completed": completed,
            "throughput_per_min": throughput,
            "eta_min": eta_min,
            "healthy": failed < total * 0.05 if total > 0 else True,
        })
    backlog = sum(r["pending"] for r in results)
    return {"queues": results, "total_queues": len(results),
            "total_backlog": backlog, "all_healthy": all(r["healthy"] for r in results)}


def get_dead_letter_queue(*, items: list[dict]) -> dict:
    return {"items": items[:50], "total": len(items),
            "oldest": items[0].get("failed_at") if items else None}
