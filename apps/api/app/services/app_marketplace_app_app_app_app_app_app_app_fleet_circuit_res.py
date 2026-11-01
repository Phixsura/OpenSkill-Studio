"""Fleet circuit resilience — track overall circuit health."""
from __future__ import annotations
def fleet_circuit_resilience(circuits: list[dict]) -> dict:
    closed = [c for c in circuits if c.get("state") == "closed"]
    trips_24h = sum(c.get("trips_24h", 0) for c in circuits)
    avg_recovery = round(sum(c.get("recovery_sec", 0) for c in circuits) / max(len(circuits), 1), 1)
    return {"total": len(circuits), "closed": len(closed), "trips_24h": trips_24h,
            "avg_recovery_sec": avg_recovery, "resilient": trips_24h < 10}
