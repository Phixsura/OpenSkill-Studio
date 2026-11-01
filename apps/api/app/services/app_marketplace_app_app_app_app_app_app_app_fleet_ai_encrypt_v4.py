"""Fleet AI Encryption v4 — track end-to-end AI data encryption."""
from __future__ import annotations
def fleet_ai_encryption_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    data_encrypted_tb = round(sum(s.get("data_tb", 0) for s in systems), 1)
    keys_managed = sum(s.get("keys", 0) for s in systems)
    rotations_24h = sum(s.get("rotations", 0) for s in systems)
    at_rest = all(s.get("at_rest", False) for s in systems)
    in_transit = all(s.get("in_transit", False) for s in systems)
    return {"systems": len(systems), "active": len(active), "data_tb": data_encrypted_tb,
            "keys": keys_managed, "rotations": rotations_24h, "at_rest": at_rest, "in_transit": in_transit, "e2e": at_rest and in_transit}
