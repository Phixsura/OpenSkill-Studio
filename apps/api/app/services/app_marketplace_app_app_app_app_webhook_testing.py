"""App webhook testing — webhook endpoint testing tools."""

import html
import json
import secrets
from datetime import datetime, timezone


def generate_test_payload(*, event_type: str = "webhook.test") -> dict:
    payload = {
        "id": f"evt_{secrets.token_hex(12)}",
        "type": event_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "data": {"test": True, "message": "This is a test webhook delivery"},
    }
    return {"payload": payload, "payload_json": json.dumps(payload, indent=2),
            "event_type": event_type, "size_bytes": len(json.dumps(payload).encode())}


def build_test_result(*, status_code: int, response_body: str = "",
                        duration_ms: int = 0, error: str = "") -> dict:
    success = 200 <= status_code < 300
    return {
        "success": success, "status_code": status_code,
        "response_preview": html.escape(response_body[:200]),
        "duration_ms": duration_ms,
        "error": html.escape(error) if error else None,
        "verdict": "✅ Webhook received successfully" if success else f"❌ Failed with status {status_code}",
    }
