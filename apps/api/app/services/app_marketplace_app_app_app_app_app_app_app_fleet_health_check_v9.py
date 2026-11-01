"""Fleet Health Check v9 — track endpoint health probes and uptime."""
from __future__ import annotations
def fleet_health_check_v9(endpoints: list[dict]) -> dict:
    up = [e for e in endpoints if e.get("status") == "up"]
    down = [e for e in endpoints if e.get("status") == "down"]
    avg_latency = sum(e.get("latency_ms", 0) for e in endpoints) / len(endpoints) if endpoints else 0
    return {"endpoints": len(endpoints), "up": len(up), "down": len(down),
            "avg_latency_ms": round(avg_latency, 1), "healthy": len(down) == 0}
