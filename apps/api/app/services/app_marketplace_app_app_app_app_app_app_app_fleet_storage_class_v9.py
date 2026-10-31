"""Fleet Storage Class v9 — track K8s storage class provisioning."""
from __future__ import annotations
def fleet_storage_class_v9(classes: list[dict]) -> dict:
    default = [c for c in classes if c.get("is_default")]
    volumes = sum(c.get("volumes", 0) for c in classes)
    total_gb = sum(c.get("total_gb", 0) for c in classes)
    return {"classes": len(classes), "default": len(default), "volumes": volumes,
            "total_gb": round(total_gb, 1), "healthy": len(default) == 1}
