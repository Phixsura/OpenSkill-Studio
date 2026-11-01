"""Fleet gateway mesh — unified gateway mesh monitoring."""
from __future__ import annotations
def fleet_gateway_mesh(gateways: list[dict]) -> dict:
    total_rps = sum(g.get("rps", 0) for g in gateways)
    healthy = [g for g in gateways if g.get("healthy", True)]
    avg_lat = round(sum(g.get("p50_ms", 0) for g in gateways) / max(len(gateways), 1), 1)
    return {"gateways": len(gateways), "healthy": len(healthy), "total_rps": total_rps,
            "avg_p50_ms": avg_lat, "all_healthy": len(healthy) == len(gateways)}
