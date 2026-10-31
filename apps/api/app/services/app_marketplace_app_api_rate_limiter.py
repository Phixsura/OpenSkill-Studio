"""API rate limiter — token bucket rate limiting implementation."""

import time
import math


def create_bucket(*, capacity: int, refill_rate: float, tokens: int | None = None) -> dict:
    return {
        "capacity": capacity,
        "refill_rate": refill_rate,
        "tokens": tokens if tokens is not None else capacity,
        "last_refill": time.time(),
    }


def try_consume(*, bucket: dict, tokens: int = 1) -> dict:
    now = time.time()
    elapsed = now - bucket["last_refill"]
    refilled = min(bucket["capacity"], bucket["tokens"] + elapsed * bucket["refill_rate"])
    if refilled >= tokens:
        new_tokens = refilled - tokens
        return {
            "allowed": True,
            "remaining": int(new_tokens),
            "capacity": bucket["capacity"],
            "retry_after_sec": 0,
        }
    else:
        deficit = tokens - refilled
        wait = math.ceil(deficit / max(bucket["refill_rate"], 0.01))
        return {
            "allowed": False,
            "remaining": 0,
            "capacity": bucket["capacity"],
            "retry_after_sec": wait,
        }


def get_rate_limit_headers(*, result: dict) -> dict:
    return {
        "X-RateLimit-Limit": str(result["capacity"]),
        "X-RateLimit-Remaining": str(result["remaining"]),
        "X-RateLimit-Reset": str(result.get("retry_after_sec", 0)),
    }
