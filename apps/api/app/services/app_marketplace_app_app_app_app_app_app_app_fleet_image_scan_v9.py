"""Fleet Image Scan v9 — track container image vulnerability scanning."""
from __future__ import annotations
def fleet_image_scan_v9(images: list[dict]) -> dict:
    scanned = [i for i in images if i.get("scanned")]
    clean = [i for i in images if i.get("vulnerabilities", 0) == 0]
    total_vulns = sum(i.get("vulnerabilities", 0) for i in images)
    return {"images": len(images), "scanned": len(scanned), "clean": len(clean),
            "total_vulnerabilities": total_vulns, "healthy": total_vulns == 0}
