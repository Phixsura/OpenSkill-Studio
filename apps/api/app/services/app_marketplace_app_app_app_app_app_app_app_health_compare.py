"""Service health comparison — compare health across time periods."""
from __future__ import annotations


def compare_health(current: dict, previous: dict) -> dict:
    changes = {}
    for key in ["uptime_pct", "error_rate_pct", "p99_ms", "incidents"]:
        cur_val = current.get(key, 0)
        prev_val = previous.get(key, 0)
        delta = round(cur_val - prev_val, 3)
        improved = delta > 0 if key == "uptime_pct" else delta < 0
        changes[key] = {"current": cur_val, "previous": prev_val,
                        "delta": delta, "improved": improved}
    overall_improved = sum(1 for c in changes.values() if c["improved"])
    return {"changes": changes, "service": current.get("service", ""),
            "overall": "improved" if overall_improved >= 3 else (
                "degraded" if overall_improved <= 1 else "stable")}
