"""Token bucket rate limiter — classic token bucket algorithm."""
from __future__ import annotations
import time

_buckets: dict[str, dict] = {}


def create_bucket(key: str, capacity: int, refill_rate: float) -> dict:
    _buckets[key] = {"key": key, "capacity": capacity, "tokens": float(capacity),
                      "refill_rate": refill_rate, "last_refill": time.time()}
    return _buckets[key]


def consume(key: str, tokens: int = 1) -> dict:
    b = _buckets.get(key)
    if not b:
        return {"allowed": False, "error": "bucket_not_found"}
    now = time.time()
    elapsed = now - b["last_refill"]
    b["tokens"] = min(b["capacity"], b["tokens"] + elapsed * b["refill_rate"])
    b["last_refill"] = now
    if b["tokens"] >= tokens:
        b["tokens"] -= tokens
        return {"allowed": True, "remaining": int(b["tokens"]),
                "capacity": b["capacity"]}
    wait = (tokens - b["tokens"]) / b["refill_rate"]
    return {"allowed": False, "remaining": int(b["tokens"]),
            "retry_after_sec": round(wait, 2)}


def bucket_status(key: str) -> dict:
    b = _buckets.get(key, {})
    return {"key": key, "tokens": int(b.get("tokens", 0)),
            "capacity": b.get("capacity", 0),
            "fill_pct": round(b.get("tokens", 0) / max(b.get("capacity", 1), 1) * 100)}


def clear_buckets() -> None:
    _buckets.clear()
