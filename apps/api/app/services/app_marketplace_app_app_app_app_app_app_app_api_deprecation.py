"""API deprecation manager — track and manage deprecated endpoints."""
from __future__ import annotations
import time


def deprecate_endpoint(path: str, method: str, sunset_date: str,
                        replacement: str = "", reason: str = "") -> dict:
    return {"path": path, "method": method.upper(), "sunset_date": sunset_date,
            "replacement": replacement, "reason": reason,
            "deprecated_at": time.time(), "status": "deprecated"}


def check_deprecated_usage(deprecated: list[dict], recent_calls: dict[str, int]) -> dict:
    active_usage = []
    total_calls = 0
    for d in deprecated:
        key = f"{d['method']} {d['path']}"
        calls = recent_calls.get(key, 0)
        if calls > 0:
            active_usage.append({**d, "recent_calls": calls})
            total_calls += calls
    return {"deprecated_in_use": len(active_usage), "total_deprecated": len(deprecated),
            "total_calls_to_deprecated": total_calls, "endpoints": active_usage,
            "action_needed": len(active_usage) > 0}


def migration_guide(deprecated: dict) -> dict:
    return {"from": f"{deprecated['method']} {deprecated['path']}",
            "to": deprecated.get("replacement", "none"),
            "reason": deprecated.get("reason", ""),
            "deadline": deprecated.get("sunset_date", ""),
            "steps": [f"Update calls from {deprecated['path']} to {deprecated.get('replacement', 'N/A')}",
                      "Test with new endpoint", "Remove old endpoint calls"]}
