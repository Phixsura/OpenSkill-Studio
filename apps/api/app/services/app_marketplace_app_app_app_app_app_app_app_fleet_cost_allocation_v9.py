"""Fleet Cost Allocation v9 — track cost allocation by tag and team."""
from __future__ import annotations
def fleet_cost_allocation_v9(allocations: list[dict]) -> dict:
    tagged = [a for a in allocations if a.get("tagged")]
    unallocated = sum(a.get("unallocated_pct", 0) for a in allocations) / len(allocations) if allocations else 0
    total = sum(a.get("monthly_cost", 0) for a in allocations)
    return {"allocations": len(allocations), "tagged": len(tagged), "unallocated_pct": round(unallocated, 1),
            "total_monthly": round(total, 2), "healthy": unallocated < 5}
