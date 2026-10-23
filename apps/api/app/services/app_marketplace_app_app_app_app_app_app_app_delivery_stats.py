"""Webhook delivery stats — aggregate delivery metrics per endpoint."""
from __future__ import annotations


def compute_delivery_stats(deliveries: list[dict]) -> dict:
    total = len(deliveries)
    success = sum(1 for d in deliveries if d.get("success"))
    failed = total - success
    success_rate = round(success / max(total, 1) * 100, 1)
    avg_latency = round(sum(d.get("latency_ms", 0) for d in deliveries) / max(total, 1), 1)
    by_status: dict[int, int] = {}
    for d in deliveries:
        code = d.get("status_code", 0)
        by_status[code] = by_status.get(code, 0) + 1
    retry_count = sum(d.get("retries", 0) for d in deliveries)
    return {
        "total": total, "success": success, "failed": failed,
        "success_rate": success_rate, "success_display": f"{success_rate}%",
        "avg_latency_ms": avg_latency,
        "by_status": dict(sorted(by_status.items())),
        "retry_count": retry_count,
        "health": "good" if success_rate >= 95 else "fair" if success_rate >= 80 else "poor",
    }
