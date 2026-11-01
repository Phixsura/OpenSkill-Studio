"""Fleet AI Circuit Breaker — track AI service resilience patterns."""
from __future__ import annotations
def fleet_ai_circuit_breaker(breakers: list[dict]) -> dict:
    closed = [b for b in breakers if b.get("state") == "closed"]
    half_open = [b for b in breakers if b.get("state") == "half_open"]
    tripped = [b for b in breakers if b.get("state") == "open"]
    total_trips = sum(b.get("trips_24h", 0) for b in breakers)
    return {"breakers": len(breakers), "closed": len(closed), "half_open": len(half_open),
            "open": len(tripped), "trips_24h": total_trips, "stable": len(tripped) == 0}
