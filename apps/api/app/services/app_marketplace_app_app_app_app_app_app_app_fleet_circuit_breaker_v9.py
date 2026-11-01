"""Fleet Circuit Breaker v9 — track circuit breaker states across services."""
from __future__ import annotations
def fleet_circuit_breaker_v9(breakers: list[dict]) -> dict:
    closed = [b for b in breakers if b.get("state") == "closed"]
    open_b = [b for b in breakers if b.get("state") == "open"]
    half_open = [b for b in breakers if b.get("state") == "half-open"]
    return {"total": len(breakers), "closed": len(closed), "open": len(open_b),
            "half_open": len(half_open), "healthy": len(open_b) == 0}
