"""Fleet API Gateway Health v9 — track gateway instance health."""
from __future__ import annotations
def fleet_api_gateway_health_v9(gateways: list[dict]) -> dict:
    healthy_g = [g for g in gateways if g.get("healthy")]
    rps = sum(g.get("rps", 0) for g in gateways)
    latency = sum(g.get("latency_ms", 0) for g in gateways) / len(gateways) if gateways else 0
    return {"gateways": len(gateways), "healthy": len(healthy_g), "total_rps": rps,
            "avg_latency_ms": round(latency, 1), "all_healthy": len(healthy_g) == len(gateways)}
