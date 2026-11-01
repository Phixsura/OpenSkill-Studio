"""Fleet Data Retention v9 — track data lifecycle and retention policies."""
from __future__ import annotations
def fleet_data_retention_v9(policies: list[dict]) -> dict:
    compliant = [p for p in policies if p.get("compliant")]
    expired_data = sum(p.get("expired_records", 0) for p in policies)
    purged = sum(p.get("purged_records", 0) for p in policies)
    return {"policies": len(policies), "compliant": len(compliant), "expired_records": expired_data,
            "purged_records": purged, "healthy": len(compliant) == len(policies)}
