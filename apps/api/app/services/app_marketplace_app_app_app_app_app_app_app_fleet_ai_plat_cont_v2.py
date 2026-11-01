"""Fleet AI Container v2 — track AI model containerization at scale."""
from __future__ import annotations
def fleet_ai_container_v2(runtimes: list[dict]) -> dict:
    active = [r for r in runtimes if r.get("active", True)]
    containers = sum(r.get("containers", 0) for r in runtimes)
    images = sum(r.get("images", 0) for r in runtimes)
    registries = sum(r.get("registries", 0) for r in runtimes)
    return {"runtimes": len(runtimes), "active": len(active), "containers": containers,
            "images": images, "registries": registries, "containerized": containers > 0}
