"""Fleet API Tracing Propagation v9 — track trace context propagation."""
from __future__ import annotations
def fleet_api_tracing_propagation_v9(services: list[dict]) -> dict:
    propagating = [s for s in services if s.get("propagation_enabled")]
    w3c = [s for s in services if s.get("format") == "w3c"]
    b3 = [s for s in services if s.get("format") == "b3"]
    return {"services": len(services), "propagating": len(propagating), "w3c": len(w3c),
            "b3": len(b3), "healthy": len(propagating) == len(services)}
