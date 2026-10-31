"""Webhook analytics — delivery analytics with success rates and latency."""

from collections import defaultdict


def build_webhook_analytics(*, deliveries: list[dict], period: str = "7d") -> dict:
    by_event: dict[str, dict] = defaultdict(lambda: {"total": 0, "success": 0, "total_ms": 0})
    for d in deliveries:
        evt = d.get("event_type", "unknown")
        by_event[evt]["total"] += 1
        if 200 <= d.get("status_code", 0) < 300:
            by_event[evt]["success"] += 1
        by_event[evt]["total_ms"] += d.get("duration_ms", 0)
    events = []
    for evt, stats in sorted(by_event.items(), key=lambda x: -x[1]["total"]):
        rate = round(stats["success"] / max(stats["total"], 1) * 100, 1)
        avg_ms = round(stats["total_ms"] / max(stats["total"], 1))
        events.append({"event": evt, "total": stats["total"], "success": stats["success"],
                        "failed": stats["total"] - stats["success"],
                        "success_rate": rate, "avg_latency_ms": avg_ms})
    total = sum(e["total"] for e in events)
    total_success = sum(e["success"] for e in events)
    return {"events": events, "total_deliveries": total,
            "overall_success_rate": round(total_success / max(total, 1) * 100, 1),
            "period": period, "event_count": len(events)}
