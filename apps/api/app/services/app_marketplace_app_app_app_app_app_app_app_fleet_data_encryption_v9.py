"""Fleet Data Encryption v9 — track encryption at rest and in transit."""
from __future__ import annotations
def fleet_data_encryption_v9(resources: list[dict]) -> dict:
    at_rest = [r for r in resources if r.get("encrypted_at_rest")]
    in_transit = [r for r in resources if r.get("encrypted_in_transit")]
    key_rotated = [r for r in resources if r.get("key_rotated_recently")]
    return {"resources": len(resources), "encrypted_at_rest": len(at_rest),
            "encrypted_in_transit": len(in_transit), "key_rotated": len(key_rotated),
            "healthy": len(at_rest) == len(resources) and len(in_transit) == len(resources)}
