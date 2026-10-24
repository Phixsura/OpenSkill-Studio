"""Retry policy — exponential backoff with jitter."""

import random
import math


def calculate_backoff(*, attempt: int, base_delay_s: float = 1.0,
                       max_delay_s: float = 60.0, jitter: bool = True) -> dict:
    delay = min(base_delay_s * (2 ** attempt), max_delay_s)
    if jitter:
        delay = random.uniform(0, delay)
    delay = round(delay, 3)
    return {"attempt": attempt, "delay_s": delay, "max_delay_s": max_delay_s,
            "capped": delay >= max_delay_s}


def build_retry_schedule(*, max_attempts: int = 5, base_delay_s: float = 1.0,
                          max_delay_s: float = 60.0) -> dict:
    schedule = []
    total = 0.0
    for i in range(max_attempts):
        delay = min(base_delay_s * (2 ** i), max_delay_s)
        total += delay
        schedule.append({"attempt": i + 1, "delay_s": round(delay, 3),
                          "cumulative_s": round(total, 3)})
    return {"schedule": schedule, "max_attempts": max_attempts,
            "total_wait_s": round(total, 3)}
