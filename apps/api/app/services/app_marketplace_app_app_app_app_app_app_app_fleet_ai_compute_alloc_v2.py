"""Fleet AI Compute Allocator v2 — track intelligent compute resource allocation."""
from __future__ import annotations
def fleet_ai_compute_allocator_v2(allocators: list[dict]) -> dict:
    active = [a for a in allocators if a.get("active", True)]
    gpus = sum(a.get("gpus", 0) for a in allocators)
    allocated = sum(a.get("allocated", 0) for a in allocators)
    efficiency = round(allocated / max(gpus, 1) * 100, 1)
    cost_optimized = round(sum(a.get("cost_saved_pct", 0) for a in allocators) / max(len(allocators), 1), 1)
    return {"allocators": len(allocators), "active": len(active), "gpus": gpus,
            "allocated": allocated, "efficiency": efficiency, "cost_saved": cost_optimized, "optimal": efficiency > 80}
