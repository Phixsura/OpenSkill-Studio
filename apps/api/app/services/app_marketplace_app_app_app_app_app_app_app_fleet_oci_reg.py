"""Fleet OCI registry — track container registry health."""
from __future__ import annotations
def fleet_oci_registry(registries: list[dict]) -> dict:
    healthy = [r for r in registries if r.get("healthy", True)]
    total_images = sum(r.get("images", 0) for r in registries)
    storage_gb = sum(r.get("storage_gb", 0) for r in registries)
    return {"registries": len(registries), "healthy": len(healthy), "images": total_images,
            "storage_gb": storage_gb, "all_healthy": len(healthy) == len(registries)}
