"""Fleet Container Image v9 — track container image lifecycle."""
from __future__ import annotations
def fleet_container_image_v9(images: list[dict]) -> dict:
    latest = [i for i in images if i.get("on_latest")]
    scanned = [i for i in images if i.get("scanned")]
    total_size = sum(i.get("size_mb", 0) for i in images)
    return {"images": len(images), "on_latest": len(latest), "scanned": len(scanned),
            "total_size_mb": round(total_size, 1), "healthy": len(scanned) == len(images)}
