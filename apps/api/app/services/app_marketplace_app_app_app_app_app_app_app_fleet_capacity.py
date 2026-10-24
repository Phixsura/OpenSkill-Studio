"""Fleet capacity planner — forecast capacity needs."""
from __future__ import annotations
def plan_fleet_capacity(services: list[dict]) -> dict:
    total_cpu = sum(s.get("cpu_pct", 0) for s in services)
    avg_cpu = round(total_cpu / max(len(services), 1), 1)
    headroom = round(100 - avg_cpu, 1)
    return {"avg_cpu_pct": avg_cpu, "headroom_pct": headroom,
            "needs_scaling": headroom < 20, "services": len(services)}
