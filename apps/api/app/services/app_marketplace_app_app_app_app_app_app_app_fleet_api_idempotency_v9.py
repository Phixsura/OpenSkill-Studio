"""Fleet API Idempotency v9 — track idempotent API request handling."""
from __future__ import annotations
def fleet_api_idempotency_v9(endpoints: list[dict]) -> dict:
    idempotent = [e for e in endpoints if e.get("idempotent")]
    duplicates_caught = sum(e.get("duplicates_caught", 0) for e in endpoints)
    keys_stored = sum(e.get("keys_stored", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "idempotent": len(idempotent),
            "duplicates_caught": duplicates_caught, "keys_stored": keys_stored,
            "healthy": len(idempotent) == len(endpoints)}
