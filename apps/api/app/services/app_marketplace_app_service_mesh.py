"""Service mesh — manage inter-service communication for marketplace platform."""


def register_service(*, service_id: str, name: str, endpoints: list[str], version: str) -> dict:
    return {"service_id": service_id, "name": name, "endpoints": endpoints,
            "version": version, "status": "registered", "health": "unknown"}


def discover_service(*, name: str, registry: list[dict]) -> dict | None:
    healthy = [s for s in registry if s["name"] == name and s.get("health") == "healthy"]
    return healthy[0] if healthy else None


def build_service_topology(*, services: list[dict], connections: list[dict]) -> dict:
    return {"nodes": [{"id": s["service_id"], "name": s["name"], "health": s.get("health")} for s in services],
            "edges": connections, "service_count": len(services), "connection_count": len(connections)}
