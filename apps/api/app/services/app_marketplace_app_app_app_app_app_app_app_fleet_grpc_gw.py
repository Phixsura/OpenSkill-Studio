"""Fleet gRPC gateway — track REST-to-gRPC transcoding."""
from __future__ import annotations
def fleet_grpc_gateway(gateways: list[dict]) -> dict:
    active = [g for g in gateways if g.get("active", True)]
    total_rps = sum(g.get("rps", 0) for g in gateways)
    transcoded = sum(g.get("transcoded_24h", 0) for g in gateways)
    return {"gateways": len(gateways), "active": len(active), "rps": total_rps,
            "transcoded_24h": transcoded, "all_active": len(active) == len(gateways)}
