"""Fleet CPU throttling — track CPU throttle events."""
from __future__ import annotations
def fleet_cpu_throttling(containers: list[dict]) -> dict:
    throttled = [c for c in containers if c.get("throttled_pct", 0) > 0]
    severe = [c for c in containers if c.get("throttled_pct", 0) > 25]
    return {"total": len(containers), "throttled": len(throttled), "severe": len(severe),
            "healthy": len(severe) == 0}
