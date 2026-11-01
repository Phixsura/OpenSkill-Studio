"""Fleet AI Rate Counter — track real-time request rate monitoring."""
from __future__ import annotations
def fleet_ai_rate_counter(counters: list[dict]) -> dict:
    active = [c for c in counters if c.get("active", True)]
    current_rps = sum(c.get("rps", 0) for c in counters)
    peak_rps = max((c.get("peak_rps", 0) for c in counters), default=0)
    windows = sum(c.get("windows", 0) for c in counters)
    return {"counters": len(counters), "active": len(active), "rps": current_rps,
            "peak_rps": peak_rps, "windows": windows, "tracking": current_rps > 0}
