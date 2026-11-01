"""Webhook payload — standardized event payload builder."""

import html
import secrets
from datetime import datetime, timezone


def build_payload(*, event_type: str, resource_type: str, resource_id: str,
                    action: str, actor: dict, data: dict | None = None) -> dict:
    return {
        "id": f"evt_{secrets.token_hex(12)}",
        "type": event_type,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "resource": {"type": resource_type, "id": resource_id},
        "action": action,
        "actor": {"id": actor.get("id", ""), "type": actor.get("type", "user"),
                   "name": html.escape(actor.get("name", ""))},
        "data": data or {},
        "api_version": "2026-01-01",
    }


def validate_payload(*, payload: dict) -> dict:
    required = ["id", "type", "created_at", "resource", "action"]
    missing = [f for f in required if f not in payload]
    return {"valid": len(missing) == 0, "missing": missing,
            "has_data": bool(payload.get("data")),
            "event_type": payload.get("type", "unknown")}
