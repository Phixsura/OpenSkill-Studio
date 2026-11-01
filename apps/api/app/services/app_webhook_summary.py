"""Webhook delivery summary — aggregate delivery stats."""


def compute_delivery_summary(deliveries: list[dict]) -> dict:
    """Compute delivery summary from a list of delivery records."""
    total = len(deliveries)
    if total == 0:
        return {"total": 0, "delivered": 0, "failed": 0, "retrying": 0, "pending": 0,
                "success_rate": 100.0, "avg_duration_ms": 0}

    by_status = {"delivered": 0, "failed": 0, "retrying": 0, "pending": 0}
    durations = []
    for d in deliveries:
        status = d.get("status", "pending")
        by_status[status] = by_status.get(status, 0) + 1
        if d.get("duration_ms"):
            durations.append(d["duration_ms"])

    success = by_status.get("delivered", 0)
    completed = success + by_status.get("failed", 0)

    return {
        "total": total,
        **by_status,
        "success_rate": round(success / completed * 100, 1) if completed > 0 else 100.0,
        "avg_duration_ms": round(sum(durations) / len(durations), 1) if durations else 0,
    }
