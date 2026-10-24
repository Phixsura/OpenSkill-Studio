"""Fleet storage class — track PV/PVC usage by storage class."""
from __future__ import annotations
def fleet_storage_class(classes: list[dict]) -> dict:
    total_gb = sum(c.get("used_gb", 0) for c in classes)
    alloc_gb = sum(c.get("allocated_gb", 1) for c in classes)
    pct = round(total_gb / max(alloc_gb, 1) * 100, 1)
    return {"used_gb": total_gb, "allocated_gb": alloc_gb, "pct": pct,
            "classes": len(classes), "pressure": pct > 80}
