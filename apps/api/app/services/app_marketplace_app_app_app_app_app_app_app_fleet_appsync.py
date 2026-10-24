"""Fleet AppSync — track GraphQL API health."""
from __future__ import annotations
def fleet_appsync_status(apis: list[dict]) -> dict:
    active = [a for a in apis if a.get("status") == "ACTIVE"]
    total_requests = sum(a.get("requests_24h", 0) for a in apis)
    errors_4xx = sum(a.get("errors_4xx", 0) for a in apis)
    errors_5xx = sum(a.get("errors_5xx", 0) for a in apis)
    return {"apis": len(apis), "active": len(active), "requests_24h": total_requests,
            "errors_4xx": errors_4xx, "errors_5xx": errors_5xx, "healthy": errors_5xx == 0}
