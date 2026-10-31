"""Fleet AI API Gateway — track unified AI API management."""
from __future__ import annotations
def fleet_ai_api_gateway(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active", True)]
    providers = sum(g.get("providers", 0) for g in gateways)
    requests_24h = sum(g.get("requests_24h", 0) for g in gateways)
    cost_24h = sum(g.get("cost_24h", 0) for g in gateways)
    return {"gateways": len(gateways), "active": len(active), "providers": providers,
            "requests_24h": requests_24h, "cost_24h": round(cost_24h, 2)}
