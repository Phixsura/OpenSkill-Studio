"""Request ID generator — generate unique, traceable request IDs."""
from __future__ import annotations
import secrets, time, hashlib


def generate_request_id(prefix: str = "req", include_timestamp: bool = True) -> dict:
    random_part = secrets.token_hex(8)
    if include_timestamp:
        ts = hex(int(time.time()))[2:]
        request_id = f"{prefix}_{ts}_{random_part}"
    else:
        request_id = f"{prefix}_{random_part}"
    return {"request_id": request_id, "prefix": prefix, "traceable": include_timestamp}


def extract_timestamp(request_id: str) -> dict:
    parts = request_id.split("_")
    if len(parts) < 3:
        return {"extracted": False}
    try:
        ts = int(parts[1], 16)
        return {"extracted": True, "timestamp": ts, "request_id": request_id}
    except ValueError:
        return {"extracted": False}


def validate_request_id(request_id: str, expected_prefix: str = "req") -> dict:
    valid = request_id.startswith(f"{expected_prefix}_") and len(request_id) >= 10
    return {"valid": valid, "request_id": request_id}
