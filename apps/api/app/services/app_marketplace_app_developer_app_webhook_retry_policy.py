"""Webhook retry policy — configurable exponential backoff retry strategies."""

import math


def create_retry_policy(*, max_retries: int = 5, initial_delay_ms: int = 1000,
                           max_delay_ms: int = 60000, backoff_multiplier: float = 2.0) -> dict:
    if max_retries < 0 or max_retries > 20:
        return {"error": "Max retries must be 0-20"}
    if initial_delay_ms < 100:
        return {"error": "Initial delay must be at least 100ms"}
    return {"max_retries": max_retries, "initial_delay_ms": initial_delay_ms,
            "max_delay_ms": max_delay_ms, "backoff_multiplier": backoff_multiplier, "error": None}


def compute_retry_delay(*, attempt: int, policy: dict) -> int:
    delay = policy["initial_delay_ms"] * (policy["backoff_multiplier"] ** attempt)
    return min(int(delay), policy["max_delay_ms"])


def build_retry_schedule(*, policy: dict) -> list[dict]:
    schedule = []
    cumulative = 0
    for i in range(policy["max_retries"]):
        delay = compute_retry_delay(attempt=i, policy=policy)
        cumulative += delay
        schedule.append({"attempt": i + 1, "delay_ms": delay, "cumulative_ms": cumulative})
    return schedule


def should_retry(*, status_code: int, attempt: int, max_retries: int) -> dict:
    retryable_codes = {408, 429, 500, 502, 503, 504}
    can_retry = status_code in retryable_codes and attempt < max_retries
    return {"should_retry": can_retry, "retryable": status_code in retryable_codes,
            "attempts_remaining": max(0, max_retries - attempt)}
