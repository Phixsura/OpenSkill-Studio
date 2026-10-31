"""Fleet image vulnerability — scan results aggregation."""
from __future__ import annotations
def fleet_img_vuln(images: list[dict]) -> dict:
    critical = sum(i.get("critical", 0) for i in images)
    high = sum(i.get("high", 0) for i in images)
    return {"images": len(images), "critical": critical, "high": high,
            "clean": critical == 0 and high == 0}
