"""Fleet Aurora — track serverless database cluster health."""
from __future__ import annotations
def fleet_aurora_status(clusters: list[dict]) -> dict:
    available = [c for c in clusters if c.get("status") == "available"]
    serverless = [c for c in clusters if c.get("serverless", False)]
    total_acu = sum(c.get("current_acu", 0) for c in serverless)
    return {"clusters": len(clusters), "available": len(available), "serverless": len(serverless),
            "current_acu": total_acu, "all_available": len(available) == len(clusters)}
