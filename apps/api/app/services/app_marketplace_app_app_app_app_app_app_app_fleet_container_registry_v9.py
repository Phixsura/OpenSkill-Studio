"""Fleet Container Registry v9 — track container image lifecycle."""
from __future__ import annotations
def fleet_container_registry_v9(images: list[dict]) -> dict:
    scanned = [i for i in images if i.get("scanned")]
    vulns = sum(i.get("vulnerabilities", 0) for i in images)
    size_gb = sum(i.get("size_mb", 0) for i in images) / 1024
    return {"total_images": len(images), "scanned": len(scanned), "vulnerabilities": vulns,
            "total_size_gb": round(size_gb, 1), "healthy": vulns == 0}
