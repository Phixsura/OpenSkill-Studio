"""Fleet API Circuit Health v9 — track circuit breaker health aggregate."""
from __future__ import annotations
def fleet_api_circuit_health_v9(circuits: list[dict]) -> dict:
    closed = [c for c in circuits if c.get("state") == "closed"]
    open_c = [c for c in circuits if c.get("state") == "open"]
    trips = sum(c.get("trips_24h", 0) for c in circuits)
    recovery = sum(c.get("auto_recovered", 0) for c in circuits)
    return {"circuits": len(circuits), "closed": len(closed), "open": len(open_c),
            "trips_24h": trips, "auto_recovered": recovery, "healthy": len(open_c) == 0}
