"""Request throttle controller — adaptive throttling by endpoint."""
from __future__ import annotations
import time

_counters: dict[str, dict] = {}


def register_endpoint(path: str, rpm_limit: int = 60) -> dict:
    _counters[path] = {"path": path, "rpm_limit": rpm_limit, "requests": [],
                        "total_served": 0, "total_throttled": 0}
    return {"registered": True, "path": path, "rpm_limit": rpm_limit}


def check_throttle(path: str) -> dict:
    c = _counters.get(path)
    if not c:
        return {"allowed": True, "reason": "unregistered"}
    now = time.time()
    c["requests"] = [t for t in c["requests"] if now - t < 60]
    if len(c["requests"]) >= c["rpm_limit"]:
        c["total_throttled"] += 1
        return {"allowed": False, "current_rpm": len(c["requests"]),
                "limit": c["rpm_limit"], "retry_after_sec": 1}
    c["requests"].append(now)
    c["total_served"] += 1
    return {"allowed": True, "current_rpm": len(c["requests"]),
            "remaining": c["rpm_limit"] - len(c["requests"])}


def throttle_stats() -> dict:
    return {path: {"served": c["total_served"], "throttled": c["total_throttled"],
                    "current_rpm": len([t for t in c["requests"] if time.time() - t < 60]),
                    "limit": c["rpm_limit"]}
            for path, c in _counters.items()}


def clear_throttle() -> None:
    _counters.clear()
