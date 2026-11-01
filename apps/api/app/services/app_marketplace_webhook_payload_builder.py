"""Webhook payload builder — construct standardized webhook payloads with metadata."""

import hashlib
import json
import time


def build_webhook_payload(*, event_type: str, data: dict, app_id: str,
                             api_version: str = "v1") -> dict:
    timestamp = int(time.time())
    payload = {"event": event_type, "api_version": api_version, "app_id": app_id,
               "data": data, "timestamp": timestamp}
    payload["id"] = f"evt_{hashlib.sha256(json.dumps(payload, sort_keys=True, default=str).encode()).hexdigest()[:12]}"
    return payload


def add_delivery_metadata(*, payload: dict, attempt: int, max_attempts: int,
                             webhook_url: str) -> dict:
    return {**payload, "delivery": {"attempt": attempt, "max_attempts": max_attempts,
            "webhook_url": webhook_url, "idempotency_key": f"{payload.get('id')}_{attempt}"}}


def validate_payload_size(*, payload: dict, max_bytes: int = 256000) -> dict:
    size = len(json.dumps(payload, default=str).encode())
    return {"size_bytes": size, "within_limit": size <= max_bytes,
            "limit_bytes": max_bytes, "usage_pct": round(size / max_bytes * 100, 1)}
