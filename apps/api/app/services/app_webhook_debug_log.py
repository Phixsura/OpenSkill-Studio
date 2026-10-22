"""Webhook debug log — detailed request/response log for debugging."""


def format_debug_entry(delivery: dict) -> dict:
    return {
        "event_type": delivery.get("event_type"),
        "url": delivery.get("url"),
        "method": "POST",
        "status_code": delivery.get("http_status"),
        "duration_ms": delivery.get("duration_ms"),
        "request_size": len(str(delivery.get("payload", ""))),
        "response_preview": str(delivery.get("response_body", ""))[:200],
        "error": delivery.get("error"),
        "timestamp": delivery.get("created_at"),
        "success": delivery.get("status") == "delivered",
    }


def format_debug_log(deliveries: list[dict]) -> list[dict]:
    return [format_debug_entry(d) for d in deliveries]
