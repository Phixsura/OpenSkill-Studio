"""Webhook log viewer — format webhook logs for developer dashboard."""


def format_webhook_log(deliveries: list[dict], *, limit: int = 50) -> dict:
    recent = deliveries[-limit:]
    success = sum(1 for d in recent if d.get("status") == "delivered")
    failed = sum(1 for d in recent if d.get("status") == "failed")
    return {
        "deliveries": recent,
        "total_shown": len(recent),
        "success_count": success,
        "failure_count": failed,
        "success_rate": round(success / len(recent) * 100, 1) if recent else 100,
    }
