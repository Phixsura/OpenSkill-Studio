"""Fleet AWS API Gateway — track managed API health."""
from __future__ import annotations
def fleet_apigw_aws_status(apis: list[dict]) -> dict:
    deployed = [a for a in apis if a.get("deployed", True)]
    total_requests = sum(a.get("requests_24h", 0) for a in apis)
    throttled = sum(a.get("throttled_24h", 0) for a in apis)
    return {"apis": len(apis), "deployed": len(deployed), "requests_24h": total_requests,
            "throttled_24h": throttled, "healthy": throttled < 100}
