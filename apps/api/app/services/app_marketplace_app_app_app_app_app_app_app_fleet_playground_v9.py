"""Fleet Playground v9 — track developer sandbox playground instances."""
from __future__ import annotations
def fleet_playground_v9(sandboxes: list[dict]) -> dict:
    active = [s for s in sandboxes if s.get("active")]
    idle = [s for s in sandboxes if not s.get("active")]
    cpu_hours = sum(s.get("cpu_hours", 0) for s in sandboxes)
    return {"total": len(sandboxes), "active": len(active), "idle": len(idle),
            "cpu_hours_today": round(cpu_hours, 1), "healthy": True}
