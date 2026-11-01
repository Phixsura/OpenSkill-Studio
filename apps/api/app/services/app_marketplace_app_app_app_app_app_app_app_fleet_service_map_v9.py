"""Fleet Service Map v9 — track real-time service dependency mapping."""
from __future__ import annotations
def fleet_service_map_v9(services: list[dict]) -> dict:
    mapped = [s for s in services if s.get("mapped")]
    connections = sum(s.get("connections", 0) for s in services)
    critical_path = [s for s in services if s.get("on_critical_path")]
    return {"services": len(services), "mapped": len(mapped), "connections": connections,
            "critical_path": len(critical_path), "healthy": len(mapped) == len(services)}
