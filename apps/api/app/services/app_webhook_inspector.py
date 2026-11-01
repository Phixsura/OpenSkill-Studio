"""Webhook inspector — detailed view of a single webhook delivery."""


def inspect_delivery(delivery: dict) -> dict:
    """Build a detailed inspection view of a webhook delivery."""
    return {
        "id": delivery.get("id"),
        "event_type": delivery.get("event_type"),
        "url": delivery.get("url"),
        "status": delivery.get("status"),
        "http_status": delivery.get("http_status"),
        "attempt": delivery.get("attempt", 1),
        "max_attempts": delivery.get("max_attempts", 5),
        "duration_ms": delivery.get("duration_ms"),
        "request_headers": delivery.get("request_headers", {}),
        "response_headers": delivery.get("response_headers", {}),
        "payload_size": len(str(delivery.get("payload", ""))),
        "error": delivery.get("error"),
        "timeline": _build_timeline(delivery),
    }


def _build_timeline(delivery: dict) -> list[dict]:
    timeline = [{"event": "created", "timestamp": delivery.get("created_at")}]
    if delivery.get("sent_at"):
        timeline.append({"event": "sent", "timestamp": delivery["sent_at"]})
    if delivery.get("delivered_at"):
        timeline.append({"event": "delivered", "timestamp": delivery["delivered_at"]})
    if delivery.get("failed_at"):
        timeline.append({"event": "failed", "timestamp": delivery["failed_at"]})
    return timeline
