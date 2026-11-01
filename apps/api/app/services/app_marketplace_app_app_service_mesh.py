"""Service mesh — service-to-service communication config."""

import html


def build_service_mesh(*, services: list[dict], policies: list[dict] | None = None) -> dict:
    nodes = []
    total_connections = 0
    for s in services:
        deps = s.get("dependencies", [])
        total_connections += len(deps)
        nodes.append({
            "name": html.escape(s.get("name", "")),
            "port": s.get("port", 80),
            "protocol": s.get("protocol", "http"),
            "health": s.get("health", "healthy"),
            "dependencies": deps,
            "dep_count": len(deps),
            "has_sidecar": s.get("sidecar", True),
        })
    mesh_policies = []
    for p in (policies or []):
        mesh_policies.append({
            "source": html.escape(p.get("source", "")),
            "destination": html.escape(p.get("destination", "")),
            "allowed": p.get("allowed", True),
            "mtls": p.get("mtls", True),
            "timeout_ms": p.get("timeout_ms", 5000),
        })
    return {"services": nodes, "service_count": len(nodes),
            "total_connections": total_connections,
            "policies": mesh_policies, "mtls_enabled": all(p.get("mtls", True) for p in mesh_policies)}
