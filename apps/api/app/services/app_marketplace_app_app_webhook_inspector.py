"""Webhook inspector — deep inspection of webhook payloads and headers."""

import html
import json
from datetime import datetime, timezone


def inspect_webhook_delivery(*, headers: dict[str, str], body: str,
                                status_code: int, duration_ms: int) -> dict:
    content_type = headers.get("content-type", "")
    is_json = "application/json" in content_type
    body_parsed = None
    if is_json:
        try:
            body_parsed = json.loads(body)
        except json.JSONDecodeError:
            pass
    safe_headers = {html.escape(k): html.escape(v) for k, v in headers.items()}
    return {
        "headers": safe_headers,
        "header_count": len(headers),
        "body_raw": html.escape(body[:2000]),
        "body_parsed": body_parsed,
        "body_size_bytes": len(body.encode()),
        "is_json": is_json,
        "status_code": status_code,
        "success": 200 <= status_code < 300,
        "duration_ms": duration_ms,
        "inspected_at": datetime.now(timezone.utc).isoformat(),
    }
