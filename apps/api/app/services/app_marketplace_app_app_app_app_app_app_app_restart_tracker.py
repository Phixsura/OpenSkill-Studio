"""Service restart tracker — monitor and alert on excessive restarts."""
from __future__ import annotations
import time


def track_restarts(services: list[dict]) -> dict:
    results = []
    crash_looping = []
    for s in services:
        restarts = s.get("restart_count", 0)
        window_min = s.get("window_min", 60)
        rate = round(restarts / max(window_min, 1) * 60, 1)  # per hour
        is_crash_loop = restarts >= 5 and rate >= 3
        if is_crash_loop:
            crash_looping.append(s["name"])
        results.append({"service": s["name"], "restarts": restarts,
                         "rate_per_hour": rate, "crash_loop": is_crash_loop})
    return {"services": results, "total": len(results),
            "crash_looping": crash_looping, "crash_loop_count": len(crash_looping),
            "all_stable": len(crash_looping) == 0}
