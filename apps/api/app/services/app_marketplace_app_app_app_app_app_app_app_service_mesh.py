"""Service mesh config — manage service-to-service communication."""
from __future__ import annotations


def create_mesh(services: list[dict]) -> dict:
    nodes = []
    connections = []
    for svc in services:
        nodes.append({"name": svc["name"], "port": svc.get("port", 8080),
                       "replicas": svc.get("replicas", 1), "healthy": svc.get("healthy", True)})
        for dep in svc.get("depends_on", []):
            connections.append({"from": svc["name"], "to": dep,
                                "protocol": svc.get("protocol", "http"),
                                "timeout_ms": svc.get("timeout_ms", 5000)})
    healthy = sum(1 for n in nodes if n["healthy"])
    return {"nodes": nodes, "connections": connections,
            "node_count": len(nodes), "connection_count": len(connections),
            "healthy": healthy, "unhealthy": len(nodes) - healthy}


def find_dependencies(mesh: dict, service_name: str) -> dict:
    direct = [c["to"] for c in mesh["connections"] if c["from"] == service_name]
    dependents = [c["from"] for c in mesh["connections"] if c["to"] == service_name]
    return {"service": service_name, "depends_on": direct,
            "depended_by": dependents, "is_leaf": len(direct) == 0,
            "is_root": len(dependents) == 0}
