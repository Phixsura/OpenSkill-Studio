"""Retry policy engine — configurable retry with exponential backoff."""
from __future__ import annotations
import math


def calculate_delay(attempt: int, base_ms: int = 1000, max_ms: int = 30000,
                    strategy: str = "exponential", jitter: bool = False) -> dict:
    if strategy == "exponential":
        delay = min(base_ms * (2 ** (attempt - 1)), max_ms)
    elif strategy == "linear":
        delay = min(base_ms * attempt, max_ms)
    elif strategy == "constant":
        delay = base_ms
    else:
        delay = base_ms
    return {"delay_ms": delay, "attempt": attempt, "strategy": strategy, "capped": delay >= max_ms}


def should_retry(status_code: int, attempt: int, max_attempts: int = 3,
                 retryable_codes: list[int] | None = None) -> dict:
    codes = retryable_codes or [429, 500, 502, 503, 504]
    if attempt >= max_attempts:
        return {"retry": False, "reason": "max_attempts_reached"}
    if status_code not in codes:
        return {"retry": False, "reason": "non_retryable_status"}
    return {"retry": True, "next_attempt": attempt + 1}


def retry_budget(total_requests: int, retried: int, budget_pct: float = 10) -> dict:
    budget = total_requests * budget_pct / 100
    remaining = max(0, budget - retried)
    exhausted = retried >= budget
    return {"budget": round(budget), "used": retried, "remaining": round(remaining),
            "exhausted": exhausted, "pct_used": round(retried / max(budget, 1) * 100, 1)}
