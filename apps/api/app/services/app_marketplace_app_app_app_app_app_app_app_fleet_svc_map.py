"""Fleet service map — visualize service topology."""
from __future__ import annotations
def fleet_service_map(services: list[dict], connections: list[dict]) -> dict:
    external = [s for s in services if s.get("external", False)]
    internal = len(services) - len(external)
    return {"services": len(services), "internal": internal, "external": len(external),
            "connections": len(connections), "avg_connections": round(len(connections) / max(len(services), 1), 1)}
