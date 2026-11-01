"""System topology — full platform topology overview."""
from __future__ import annotations


def build_system_topology(layers: dict[str, list[dict]]) -> dict:
    total_services = 0
    total_connections = 0
    layer_stats = {}
    for layer_name, services in layers.items():
        healthy = sum(1 for s in services if s.get("status") == "healthy")
        conns = sum(len(s.get("connections", [])) for s in services)
        total_services += len(services)
        total_connections += conns
        layer_stats[layer_name] = {"services": len(services), "healthy": healthy, "connections": conns}
    return {"layers": layer_stats, "total_services": total_services,
            "total_connections": total_connections, "layer_count": len(layers)}
