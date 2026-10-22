"""Webhook backoff calculator — compute retry delays with jitter."""

import random
import math

def compute_backoff(attempt: int, *, base_seconds: float = 10, max_seconds: float = 3600, jitter: bool = True) -> float:
    """Exponential backoff: base * 2^attempt, capped at max, with optional jitter."""
    delay = min(base_seconds * (2 ** attempt), max_seconds)
    if jitter:
        delay = delay * (0.5 + random.random() * 0.5)  # noqa: S311
    return round(delay, 2)

def compute_schedule(max_attempts: int = 5, **kwargs) -> list[float]:
    return [compute_backoff(i, **kwargs) for i in range(max_attempts)]

def total_delay(max_attempts: int = 5, **kwargs) -> float:
    return sum(compute_schedule(max_attempts, jitter=False, **kwargs))
