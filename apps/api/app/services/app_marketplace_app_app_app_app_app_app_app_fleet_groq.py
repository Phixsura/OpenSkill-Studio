"""Fleet Groq — track LPU inference engine."""
from __future__ import annotations
def fleet_groq_status(endpoints: list[dict]) -> dict:
    active = [e for e in endpoints if e.get("active", True)]
    tokens_per_sec = sum(e.get("tokens_per_sec", 0) for e in endpoints)
    requests_24h = sum(e.get("requests_24h", 0) for e in endpoints)
    return {"endpoints": len(endpoints), "active": len(active), "tokens_per_sec": tokens_per_sec,
            "requests_24h": requests_24h, "blazing": tokens_per_sec > 500}
