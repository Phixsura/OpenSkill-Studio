"""Platform capacity dashboard — monitor resource capacity across the fleet."""
from __future__ import annotations


def capacity_overview(resources: list[dict]) -> dict:
    total_capacity = 0
    total_used = 0
    critical = []
    for r in resources:
        cap = r.get("capacity", 0)
        used = r.get("used", 0)
        total_capacity += cap
        total_used += used
        pct = round(used / max(cap, 1) * 100, 1)
        if pct >= 85:
            critical.append({"name": r["name"], "type": r.get("type", ""), "pct": pct})
    overall_pct = round(total_used / max(total_capacity, 1) * 100, 1)
    return {"total_capacity": total_capacity, "total_used": total_used,
            "overall_pct": overall_pct, "critical": critical,
            "critical_count": len(critical), "resource_count": len(resources),
            "status": "critical" if critical else "healthy"}
