"""Fleet API Composition v9 — track API gateway request composition."""
from __future__ import annotations
def fleet_api_composition_v9(compositions: list[dict]) -> dict:
    active = [c for c in compositions if c.get("active")]
    backends = sum(c.get("backends", 0) for c in compositions)
    avg_latency = sum(c.get("avg_latency_ms", 0) for c in compositions) / len(compositions) if compositions else 0
    return {"compositions": len(compositions), "active": len(active), "total_backends": backends,
            "avg_latency_ms": round(avg_latency, 1), "healthy": avg_latency < 200}
