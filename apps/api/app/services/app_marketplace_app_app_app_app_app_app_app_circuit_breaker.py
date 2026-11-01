"""Circuit breaker — protect services from cascading failures."""
from __future__ import annotations
import time

_breakers: dict[str, dict] = {}


def create_breaker(name: str, failure_threshold: int = 5, recovery_sec: int = 30) -> dict:
    _breakers[name] = {"name": name, "state": "closed", "failures": 0,
                        "threshold": failure_threshold, "recovery_sec": recovery_sec,
                        "last_failure": 0.0, "total_trips": 0}
    return _breakers[name]


def record_result(name: str, success: bool) -> dict:
    b = _breakers.get(name)
    if not b:
        return {"error": "unknown_breaker"}
    now = time.time()
    if b["state"] == "open":
        if now - b["last_failure"] >= b["recovery_sec"]:
            b["state"] = "half_open"
        else:
            return {"state": b["state"], "allowed": False}
    if success:
        if b["state"] == "half_open":
            b["state"] = "closed"
        b["failures"] = 0
    else:
        b["failures"] += 1
        b["last_failure"] = now
        if b["failures"] >= b["threshold"]:
            b["state"] = "open"
            b["total_trips"] += 1
    return {"state": b["state"], "failures": b["failures"], "allowed": b["state"] != "open"}


def get_status(name: str) -> dict:
    b = _breakers.get(name, {})
    return {"name": name, "state": b.get("state", "unknown"),
            "failures": b.get("failures", 0), "total_trips": b.get("total_trips", 0)}


def clear_breakers() -> None:
    _breakers.clear()
