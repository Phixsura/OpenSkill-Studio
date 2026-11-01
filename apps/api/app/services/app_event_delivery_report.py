"""Event delivery report — summarize delivery stats per event type."""

from collections import defaultdict


def compute_delivery_report(deliveries: list[dict]) -> dict:
    """Compute delivery report grouped by event type."""
    by_type: dict[str, dict] = defaultdict(lambda: {"total": 0, "delivered": 0, "failed": 0})
    for d in deliveries:
        et = d.get("event_type", "unknown")
        by_type[et]["total"] += 1
        if d.get("status") == "delivered":
            by_type[et]["delivered"] += 1
        elif d.get("status") == "failed":
            by_type[et]["failed"] += 1

    result = []
    for event_type, stats in sorted(by_type.items()):
        rate = round(stats["delivered"] / stats["total"] * 100, 1) if stats["total"] > 0 else 0
        result.append({"event_type": event_type, **stats, "success_rate": rate})
    return {"event_types": result, "total_deliveries": sum(s["total"] for s in by_type.values())}
