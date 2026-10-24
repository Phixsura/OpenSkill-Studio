"""Fleet MinIO — track object storage health."""
from __future__ import annotations
def fleet_minio_status(servers: list[dict]) -> dict:
    online = [s for s in servers if s.get("online", True)]
    total_tb = sum(s.get("storage_tb", 0) for s in servers)
    used_tb = sum(s.get("used_tb", 0) for s in servers)
    pct = round(used_tb / max(total_tb, 0.01) * 100, 1)
    return {"servers": len(servers), "online": len(online), "total_tb": total_tb,
            "used_tb": round(used_tb, 1), "usage_pct": pct, "healthy": len(online) == len(servers)}
