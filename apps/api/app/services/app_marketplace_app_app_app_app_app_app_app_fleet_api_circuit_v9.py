"""Fleet API Circuit v9 — track per-API circuit breaker states."""
from __future__ import annotations
def fleet_api_circuit_v9(circuits: list[dict]) -> dict:
    closed = [c for c in circuits if c.get("state") == "closed"]
    open_c = [c for c in circuits if c.get("state") == "open"]
    half_open = [c for c in circuits if c.get("state") == "half-open"]
    trips_today = sum(c.get("trips_today", 0) for c in circuits)
    return {"circuits": len(circuits), "closed": len(closed), "open": len(open_c),
            "half_open": len(half_open), "trips_today": trips_today, "healthy": len(open_c) == 0}
