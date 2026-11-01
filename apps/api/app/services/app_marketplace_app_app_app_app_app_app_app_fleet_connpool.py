"""Fleet connection pool — track DB connection pool utilization."""
from __future__ import annotations
def fleet_connpool(services: list[dict]) -> dict:
    used = sum(s.get("conns_used", 0) for s in services)
    total = sum(s.get("conns_max", 1) for s in services)
    pct = round(used / max(total, 1) * 100, 1)
    return {"used": used, "max": total, "pct": pct, "saturated": pct > 85}
