"""Fleet Live Debug v9 — track live debugging sessions and breakpoints."""
from __future__ import annotations
def fleet_live_debug_v9(sessions: list[dict]) -> dict:
    active = [s for s in sessions if s.get("active")]
    breakpoints = sum(s.get("breakpoints", 0) for s in sessions)
    avg_duration = sum(s.get("duration_min", 0) for s in sessions) / len(sessions) if sessions else 0
    return {"sessions": len(sessions), "active": len(active), "breakpoints": breakpoints,
            "avg_duration_min": round(avg_duration, 1), "healthy": True}
