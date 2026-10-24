"""Fleet AI Platform Gateway — track unified AI platform API gateway."""
from __future__ import annotations
def fleet_ai_platform_gateway(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active", True)]
    routes = sum(g.get("routes", 0) for g in gateways)
    requests_24h = sum(g.get("requests_24h", 0) for g in gateways)
    p99_ms = round(sum(g.get("p99_ms", 0) for g in gateways) / max(len(gateways), 1), 1)
    return {"gateways": len(gateways), "active": len(active), "routes": routes,
            "requests_24h": requests_24h, "p99_ms": p99_ms, "fast": p99_ms < 50}
