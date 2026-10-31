"""Fleet API gateway health — aggregate gateway health metrics."""
from __future__ import annotations
def fleet_apigw_health(gateways: list[dict]) -> dict:
    healthy = [g for g in gateways if g.get("status") == "healthy"]
    total_rps = sum(g.get("rps", 0) for g in gateways)
    avg_lat = round(sum(g.get("latency_ms", 0) for g in gateways) / max(len(gateways), 1), 1)
    return {"gateways": len(gateways), "healthy": len(healthy), "total_rps": total_rps,
            "avg_latency_ms": avg_lat, "all_healthy": len(healthy) == len(gateways)}
