"""Retry policy engine — configurable retry with backoff strategies."""
from __future__ import annotations
import math


def create_policy(max_retries: int = 3, backoff: str = "exponential",
                  base_delay_ms: int = 1000, max_delay_ms: int = 30000,
                  retryable_codes: list[int] | None = None) -> dict:
    valid_backoffs = {"exponential", "linear", "constant"}
    if backoff not in valid_backoffs:
        return {"created": False, "error": f"invalid backoff, use {sorted(valid_backoffs)}"}
    return {"created": True, "max_retries": max_retries, "backoff": backoff,
            "base_delay_ms": base_delay_ms, "max_delay_ms": max_delay_ms,
            "retryable_codes": retryable_codes or [429, 500, 502, 503, 504]}


def compute_delay(policy: dict, attempt: int) -> dict:
    if attempt >= policy["max_retries"]:
        return {"should_retry": False, "reason": "max_retries_exceeded"}
    base = policy["base_delay_ms"]
    if policy["backoff"] == "exponential":
        delay = min(base * (2 ** attempt), policy["max_delay_ms"])
    elif policy["backoff"] == "linear":
        delay = min(base * (attempt + 1), policy["max_delay_ms"])
    else:
        delay = base
    return {"should_retry": True, "delay_ms": delay, "attempt": attempt + 1,
            "next_attempt": attempt + 1}


def should_retry(policy: dict, status_code: int, attempt: int) -> dict:
    if attempt >= policy["max_retries"]:
        return {"retry": False, "reason": "exhausted"}
    if status_code not in policy["retryable_codes"]:
        return {"retry": False, "reason": "non_retryable"}
    d = compute_delay(policy, attempt)
    return {"retry": True, "delay_ms": d["delay_ms"], "attempt": attempt + 1}
