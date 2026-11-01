"""Fleet Harbor Registry v9 — track Harbor container registry instances."""
from __future__ import annotations
def fleet_harbor_registry_v9(registries: list[dict]) -> dict:
    healthy_r = [r for r in registries if r.get("healthy")]
    projects = sum(r.get("projects", 0) for r in registries)
    images = sum(r.get("images", 0) for r in registries)
    return {"registries": len(registries), "healthy": len(healthy_r), "projects": projects,
            "images": images, "all_healthy": len(healthy_r) == len(registries)}
