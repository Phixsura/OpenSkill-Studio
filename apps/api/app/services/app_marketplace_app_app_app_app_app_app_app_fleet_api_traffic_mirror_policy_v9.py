"""Fleet API Traffic Mirror Policy v9 — track shadow testing policies."""
from __future__ import annotations
def fleet_api_traffic_mirror_policy_v9(policies: list[dict]) -> dict:
    active = [p for p in policies if p.get("active")]
    mirrored_rps = sum(p.get("mirrored_rps", 0) for p in policies)
    discrepancies = sum(p.get("discrepancies", 0) for p in policies)
    return {"policies": len(policies), "active": len(active), "mirrored_rps": mirrored_rps,
            "discrepancies": discrepancies, "healthy": discrepancies < 10}
