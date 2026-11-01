"""Idempotency key — prevent duplicate API operations."""

import secrets
import hashlib
from datetime import datetime, timedelta


def generate_idempotency_key(*, prefix: str = "idem") -> dict:
    key = f"{prefix}_{secrets.token_urlsafe(16)}"
    return {"key": key, "expires_at": (datetime.utcnow() + timedelta(hours=24)).isoformat()}


def check_idempotency(*, key: str, cache: dict[str, dict]) -> dict:
    if key in cache:
        cached = cache[key]
        return {"duplicate": True, "original_response": cached.get("response"),
                "created_at": cached.get("created_at"), "status": "cached"}
    return {"duplicate": False, "status": "new"}


def compute_request_hash(*, method: str, path: str, body: str | None = None) -> dict:
    payload = f"{method}:{path}:{body or ''}"
    request_hash = hashlib.sha256(payload.encode()).hexdigest()[:24]
    return {"hash": request_hash, "method": method, "path": path}
