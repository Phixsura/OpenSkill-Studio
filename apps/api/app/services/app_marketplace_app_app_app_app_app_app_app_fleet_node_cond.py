"""Fleet node condition — track node health conditions."""
from __future__ import annotations
def fleet_node_conditions(nodes: list[dict]) -> dict:
    not_ready = [n for n in nodes if not n.get("ready", True)]
    pressure = [n for n in nodes if n.get("disk_pressure", False) or n.get("memory_pressure", False)]
    return {"total": len(nodes), "not_ready": len(not_ready),
            "pressure": len(pressure), "all_healthy": len(not_ready) == 0 and len(pressure) == 0}
