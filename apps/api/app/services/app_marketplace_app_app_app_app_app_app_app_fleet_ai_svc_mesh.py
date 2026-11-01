"""Fleet AI Service Mesh — track AI microservice communication."""
from __future__ import annotations
def fleet_ai_service_mesh(meshes: list[dict]) -> dict:
    active = [m for m in meshes if m.get("active", True)]
    services = sum(m.get("services", 0) for m in meshes)
    requests_24h = sum(m.get("requests_24h", 0) for m in meshes)
    p99_ms = round(sum(m.get("p99_ms", 0) for m in meshes) / max(len(meshes), 1), 1)
    return {"meshes": len(meshes), "active": len(active), "services": services,
            "requests_24h": requests_24h, "p99_ms": p99_ms, "fast": p99_ms < 100}
