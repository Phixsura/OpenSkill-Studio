"""Fleet resource quota — track namespace resource quota usage."""
from __future__ import annotations
def fleet_resource_quota(namespaces: list[dict]) -> dict:
    over = [n for n in namespaces if n.get("cpu_used_pct", 0) > 80 or n.get("mem_used_pct", 0) > 80]
    return {"total": len(namespaces), "over_threshold": len(over),
            "within": len(namespaces) - len(over), "healthy": len(over) == 0}
