"""Fleet memory utilization — track memory across services."""
from __future__ import annotations
def fleet_memory_utilization(services: list[dict]) -> dict:
    total_used = sum(s.get("mem_used_mb", 0) for s in services)
    total_alloc = sum(s.get("mem_alloc_mb", 1) for s in services)
    pct = round(total_used / max(total_alloc, 1) * 100, 1)
    return {"used_mb": total_used, "allocated_mb": total_alloc, "pct": pct, "pressure": pct > 85}
