"""Fleet AI Health Check — track deep AI service health probes."""
from __future__ import annotations
def fleet_ai_health_check(probes: list[dict]) -> dict:
    healthy = [p for p in probes if p.get("status") == "healthy"]
    degraded = [p for p in probes if p.get("status") == "degraded"]
    down = [p for p in probes if p.get("status") == "down"]
    avg_latency = round(sum(p.get("latency_ms", 0) for p in probes) / max(len(probes), 1), 1)
    return {"probes": len(probes), "healthy": len(healthy), "degraded": len(degraded),
            "down": len(down), "avg_latency_ms": avg_latency, "all_green": len(down) == 0 and len(degraded) == 0}
