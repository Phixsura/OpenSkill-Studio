"""Retry policy engine — configurable retry strategies with backoff."""
from __future__ import annotations
import math


def compute_delay(*, attempt: int, strategy: str = "exponential",
                   base_delay_ms: int = 1000, max_delay_ms: int = 30000,
                   jitter: bool = True, jitter_factor: float = 0.1) -> dict:
    if strategy == "exponential":
        delay = min(base_delay_ms * (2 ** (attempt - 1)), max_delay_ms)
    elif strategy == "linear":
        delay = min(base_delay_ms * attempt, max_delay_ms)
    elif strategy == "fixed":
        delay = base_delay_ms
    else:
        return {"error": f"Unknown strategy: {strategy}"}
    jitter_ms = int(delay * jitter_factor) if jitter else 0
    return {"attempt": attempt, "delay_ms": delay, "jitter_ms": jitter_ms,
            "total_ms": delay + jitter_ms,
            "delay_display": f"{(delay + jitter_ms) / 1000:.1f}s",
            "strategy": strategy, "capped": delay >= max_delay_ms}


def build_retry_schedule(*, max_attempts: int = 5, strategy: str = "exponential",
                          base_delay_ms: int = 1000, max_delay_ms: int = 30000) -> dict:
    schedule = []
    total_wait = 0
    for i in range(1, max_attempts + 1):
        d = compute_delay(attempt=i, strategy=strategy, base_delay_ms=base_delay_ms,
                          max_delay_ms=max_delay_ms, jitter=False)
        total_wait += d["delay_ms"]
        schedule.append(d)
    return {"max_attempts": max_attempts, "strategy": strategy,
            "schedule": schedule, "total_wait_ms": total_wait,
            "total_wait_display": f"{total_wait / 1000:.1f}s"}
