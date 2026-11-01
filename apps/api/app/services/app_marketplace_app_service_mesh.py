"""Service mesh — manage service-to-service communication."""


def build_service_topology(*, services: list[dict]) -> dict:
    nodes = []
    edges = []
    for svc in services:
        nodes.append({"id": svc["id"], "name": svc["name"], "type": svc.get("type", "service"),
                       "healthy": svc.get("healthy", True)})
        for dep in svc.get("depends_on", []):
            edges.append({"from": svc["id"], "to": dep, "protocol": "grpc"})
    healthy_count = sum(1 for n in nodes if n["healthy"])
    return {
        "nodes": nodes,
        "edges": edges,
        "total_services": len(nodes),
        "healthy_services": healthy_count,
        "total_connections": len(edges),
        "mesh_health": "healthy" if healthy_count == len(nodes) else "degraded",
    }


def get_traffic_policy(*, service_id: str) -> dict:
    return {
        "service_id": service_id,
        "retry_policy": {"max_retries": 3, "retry_on": ["5xx", "reset", "connect-failure"]},
        "circuit_breaker": {"threshold": 5, "interval_sec": 30, "min_requests": 10},
        "timeout_ms": 5000,
        "load_balancing": "round_robin",
        "rate_limit": {"requests_per_sec": 100, "burst": 150},
    }
