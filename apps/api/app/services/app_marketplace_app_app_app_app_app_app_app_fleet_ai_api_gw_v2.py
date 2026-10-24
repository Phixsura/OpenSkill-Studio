"""Fleet AI API Gateway v2 — track next-gen AI API gateway management."""
from __future__ import annotations
def fleet_ai_api_gateway_v2(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active", True)]
    routes = sum(g.get("routes", 0) for g in gateways)
    requests_24h = sum(g.get("requests_24h", 0) for g in gateways)
    auth_methods = sum(g.get("auth_methods", 0) for g in gateways)
    return {"gateways": len(gateways), "active": len(active), "routes": routes,
            "requests_24h": requests_24h, "auth_methods": auth_methods, "secure": auth_methods > 2}
