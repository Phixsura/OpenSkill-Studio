"""Fleet AI Encryption v8 — track ultimate end-to-end encryption."""
from __future__ import annotations
def fleet_ai_encrypt_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    data_eb = round(sum(s.get("data_eb", 0) for s in systems), 1)
    keys = sum(s.get("keys", 0) for s in systems)
    at_rest = all(s.get("at_rest", False) for s in systems)
    in_transit = all(s.get("in_transit", False) for s in systems)
    return {"systems": len(systems), "active": len(active), "data_eb": data_eb,
            "keys": keys, "e2e": at_rest and in_transit, "quantum_safe": all(s.get("quantum", False) for s in systems)}
