"""Fleet scaling decision — recommend scale up/down/steady."""
from __future__ import annotations
def fleet_scaling_decision(cpu_pct: float, mem_pct: float, queue_depth: int) -> dict:
    if cpu_pct > 80 or mem_pct > 85 or queue_depth > 1000:
        action = "scale_up"
    elif cpu_pct < 30 and mem_pct < 40 and queue_depth < 10:
        action = "scale_down"
    else:
        action = "steady"
    return {"cpu_pct": cpu_pct, "mem_pct": mem_pct, "queue_depth": queue_depth, "action": action}
