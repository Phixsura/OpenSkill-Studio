"""Webhook event builder — construct well-formed webhook event payloads."""

import hashlib
import json
import time


def build_event(*, event_type: str, app_id: str, data: dict, source: str = "marketplace") -> dict:
    timestamp = int(time.time())
    payload = {"event": event_type, "app_id": app_id, "data": data,
               "source": source, "timestamp": timestamp}
    event_id = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:16]
    return {"id": f"evt_{event_id}", **payload}


def validate_event_payload(*, event: dict) -> dict:
    required = {"event", "app_id", "data", "timestamp"}
    missing = required - set(event.keys())
    if missing:
        return {"valid": False, "errors": [f"Missing field: {f}" for f in missing]}
    if not isinstance(event.get("data"), dict):
        return {"valid": False, "errors": ["'data' must be an object"]}
    return {"valid": True, "errors": []}


def serialize_event(*, event: dict, format: str = "json") -> str:
    if format == "json":
        return json.dumps(event, default=str)
    return "\n".join(f"{k}={v}" for k, v in event.items())
