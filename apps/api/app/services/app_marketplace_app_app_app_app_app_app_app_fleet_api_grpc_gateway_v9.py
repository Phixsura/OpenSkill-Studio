"""Fleet API gRPC Gateway v9 — track gRPC-JSON transcoding gateway."""
from __future__ import annotations
def fleet_api_grpc_gateway_v9(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active")]
    transcoded = sum(g.get("requests_today", 0) for g in gateways)
    methods = sum(g.get("methods", 0) for g in gateways)
    return {"gateways": len(gateways), "active": len(active), "transcoded_today": transcoded,
            "methods": methods, "healthy": len(active) == len(gateways)}
