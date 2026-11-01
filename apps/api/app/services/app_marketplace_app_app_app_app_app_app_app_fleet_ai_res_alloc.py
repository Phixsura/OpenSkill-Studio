"""Fleet AI Resource Allocator — track compute resource allocation optimization."""
from __future__ import annotations
def fleet_ai_resource_allocator(allocators: list[dict]) -> dict:
    active = [a for a in allocators if a.get("active", True)]
    total_gpus = sum(a.get("gpus", 0) for a in allocators)
    allocated = sum(a.get("allocated", 0) for a in allocators)
    waste_pct = round(sum(a.get("waste_pct", 0) for a in allocators) / max(len(allocators), 1), 1)
    return {"allocators": len(allocators), "active": len(active), "gpus": total_gpus,
            "allocated": allocated, "waste_pct": waste_pct, "efficient": waste_pct < 10}
