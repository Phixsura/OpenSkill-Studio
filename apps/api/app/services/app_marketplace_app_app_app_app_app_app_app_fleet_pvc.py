"""Fleet PVC — track persistent volume claim status."""
from __future__ import annotations
def fleet_pvc_status(pvcs: list[dict]) -> dict:
    bound = [p for p in pvcs if p.get("status") == "Bound"]
    pending = [p for p in pvcs if p.get("status") == "Pending"]
    lost = [p for p in pvcs if p.get("status") == "Lost"]
    return {"total": len(pvcs), "bound": len(bound), "pending": len(pending),
            "lost": len(lost), "healthy": len(pending) == 0 and len(lost) == 0}
