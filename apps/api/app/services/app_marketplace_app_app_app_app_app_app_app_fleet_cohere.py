"""Fleet Cohere — track enterprise AI platform."""
from __future__ import annotations
def fleet_cohere_status(endpoints: list[dict]) -> dict:
    active = [e for e in endpoints if e.get("active", True)]
    embed_calls = sum(e.get("embed_calls_24h", 0) for e in endpoints)
    generate_calls = sum(e.get("generate_calls_24h", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "active": len(active), "embed_calls": embed_calls,
            "generate_calls": generate_calls, "all_active": len(active) == len(endpoints)}
