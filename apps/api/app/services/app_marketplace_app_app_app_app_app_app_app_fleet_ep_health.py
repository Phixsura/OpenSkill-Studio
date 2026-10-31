"""Fleet endpoint health — aggregate endpoint availability."""
from __future__ import annotations
def fleet_endpoint_health(endpoints: list[dict]) -> dict:
    up = [e for e in endpoints if e.get("status") == "up"]
    degraded = [e for e in endpoints if e.get("status") == "degraded"]
    down = [e for e in endpoints if e.get("status") == "down"]
    avail = round(len(up) / max(len(endpoints), 1) * 100, 1)
    return {"total": len(endpoints), "up": len(up), "degraded": len(degraded),
            "down": len(down), "availability_pct": avail}
