"""Fleet time-to-value — measure how fast users get value."""
from __future__ import annotations
def fleet_time_to_value(users: list[dict]) -> dict:
    times = [u.get("ttv_hours", 0) for u in users]
    avg = round(sum(times) / max(len(times), 1), 1)
    fast = [t for t in times if t <= 24]
    return {"total": len(users), "avg_ttv_hours": avg, "fast_activation": len(fast),
            "fast_pct": round(len(fast) / max(len(users), 1) * 100, 1)}
