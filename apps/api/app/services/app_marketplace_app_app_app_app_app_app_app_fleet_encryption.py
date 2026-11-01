"""Fleet data encryption — track encryption at rest and in transit."""
from __future__ import annotations
def fleet_encryption_status(services: list[dict]) -> dict:
    at_rest = [s for s in services if s.get("encryption_at_rest", False)]
    in_transit = [s for s in services if s.get("encryption_in_transit", False)]
    both = [s for s in services if s.get("encryption_at_rest") and s.get("encryption_in_transit")]
    return {"total": len(services), "at_rest": len(at_rest), "in_transit": len(in_transit),
            "both": len(both), "fully_encrypted": len(both) == len(services)}
