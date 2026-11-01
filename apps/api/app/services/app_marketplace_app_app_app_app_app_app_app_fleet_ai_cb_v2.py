"""Fleet AI Circuit Breaker v2 — track advanced resilience patterns."""
from __future__ import annotations
def fleet_ai_circuit_breaker_v2(breakers: list[dict]) -> dict:
    active = [b for b in breakers if b.get("active", True)]
    closed = sum(1 for b in breakers if b.get("state") == "closed")
    half_open = sum(1 for b in breakers if b.get("state") == "half_open")
    open_count = sum(1 for b in breakers if b.get("state") == "open")
    trips_24h = sum(b.get("trips_24h", 0) for b in breakers)
    return {"breakers": len(breakers), "active": len(active), "closed": closed,
            "half_open": half_open, "open": open_count, "trips_24h": trips_24h, "stable": open_count == 0}
