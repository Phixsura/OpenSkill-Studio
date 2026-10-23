"""Webhook retry policy — configure retry strategies for failed deliveries."""

import math


def create_retry_policy(*, strategy: str = "exponential", max_retries: int = 5,
                          initial_delay_sec: int = 10, max_delay_sec: int = 3600) -> dict:
    valid_strategies = {"exponential", "linear", "fixed"}
    if strategy not in valid_strategies:
        return {"error": f"Invalid strategy. Valid: {', '.join(sorted(valid_strategies))}"}
    if max_retries > 20:
        return {"error": "Max retries cannot exceed 20"}
    schedule = []
    for attempt in range(1, max_retries + 1):
        if strategy == "exponential":
            delay = min(initial_delay_sec * (2 ** (attempt - 1)), max_delay_sec)
        elif strategy == "linear":
            delay = min(initial_delay_sec * attempt, max_delay_sec)
        else:
            delay = initial_delay_sec
        schedule.append({"attempt": attempt, "delay_sec": delay,
                          "delay_formatted": f"{delay // 60}m {delay % 60}s" if delay >= 60 else f"{delay}s"})
    total_time = sum(s["delay_sec"] for s in schedule)
    return {
        "strategy": strategy,
        "max_retries": max_retries,
        "schedule": schedule,
        "total_retry_window_sec": total_time,
        "total_retry_window_formatted": f"{total_time // 3600}h {(total_time % 3600) // 60}m",
    }
