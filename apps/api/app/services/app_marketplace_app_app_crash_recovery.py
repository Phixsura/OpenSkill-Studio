"""Crash recovery — automated crash detection and recovery procedures."""

import secrets
from datetime import datetime


def detect_crash(*, health_checks: list[dict], threshold: int = 3) -> dict:
    consecutive_failures = 0
    for check in reversed(health_checks):
        if check.get("status") == "fail":
            consecutive_failures += 1
        else:
            break
    crashed = consecutive_failures >= threshold
    return {
        "crashed": crashed,
        "consecutive_failures": consecutive_failures,
        "threshold": threshold,
        "last_check": health_checks[-1] if health_checks else None,
        "recovery_needed": crashed,
    }


def create_recovery_plan(*, app_id: str, crash_type: str) -> dict:
    plans = {
        "oom": ["Restart with increased memory", "Analyze memory leak", "Scale horizontally"],
        "deadlock": ["Force restart", "Clear connection pool", "Check query locks"],
        "unresponsive": ["Restart app", "Check CPU usage", "Review recent deploy"],
        "boot_failure": ["Rollback to previous version", "Check config changes", "Review logs"],
    }
    steps = plans.get(crash_type, ["Restart app", "Check logs", "Contact support"])
    return {
        "recovery_id": f"rcv_{secrets.token_urlsafe(8)}",
        "app_id": app_id,
        "crash_type": crash_type,
        "steps": [{"step": i+1, "action": s, "status": "pending"} for i, s in enumerate(steps)],
        "auto_recovery": crash_type in ("oom", "unresponsive"),
        "created_at": datetime.utcnow().isoformat(),
    }
