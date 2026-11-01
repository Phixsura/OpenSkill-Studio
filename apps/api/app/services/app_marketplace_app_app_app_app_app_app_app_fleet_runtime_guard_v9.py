"""Fleet Runtime Guard v9 — track runtime security enforcement."""
from __future__ import annotations
def fleet_runtime_guard_v9(guards: list[dict]) -> dict:
    active = [g for g in guards if g.get("active")]
    blocked = sum(g.get("blocked_today", 0) for g in guards)
    processes_monitored = sum(g.get("processes", 0) for g in guards)
    return {"guards": len(guards), "active": len(active), "blocked_today": blocked,
            "processes_monitored": processes_monitored, "healthy": True}
