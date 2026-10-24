"""Throttle manager — adaptive throttling based on system load."""

import time


def calculate_throttle(*, current_rps: float, max_rps: float,
                         cpu_usage: float, memory_usage: float) -> dict:
    load_factor = max(cpu_usage, memory_usage) / 100
    effective_max = max_rps * (1 - max(load_factor - 0.7, 0) * 2)
    throttled = current_rps > effective_max
    delay_ms = 0
    if throttled:
        overage_pct = (current_rps - effective_max) / max(effective_max, 1) * 100
        delay_ms = min(int(overage_pct * 10), 5000)
    return {
        "current_rps": current_rps,
        "max_rps": max_rps,
        "effective_max_rps": round(effective_max, 1),
        "throttled": throttled,
        "delay_ms": delay_ms,
        "load_factor": round(load_factor, 2),
        "recommendation": "shed_load" if load_factor > 0.9 else "throttle" if throttled else "normal",
    }


def get_throttle_config(*, tier: str = "standard") -> dict:
    configs = {
        "free": {"max_rps": 10, "burst": 20, "window_sec": 60},
        "standard": {"max_rps": 100, "burst": 200, "window_sec": 60},
        "premium": {"max_rps": 1000, "burst": 2000, "window_sec": 60},
        "enterprise": {"max_rps": 10000, "burst": 20000, "window_sec": 60},
    }
    return configs.get(tier, configs["standard"])
