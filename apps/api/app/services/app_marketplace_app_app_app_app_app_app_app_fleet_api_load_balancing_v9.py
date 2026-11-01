"""Fleet API Load Balancing v9 — track API load balancing algorithms."""
from __future__ import annotations
def fleet_api_load_balancing_v9(lbs: list[dict]) -> dict:
    round_robin = [l for l in lbs if l.get("algorithm") == "round_robin"]
    least_conn = [l for l in lbs if l.get("algorithm") == "least_connections"]
    weighted = [l for l in lbs if l.get("algorithm") == "weighted"]
    rps = sum(l.get("rps", 0) for l in lbs)
    return {"load_balancers": len(lbs), "round_robin": len(round_robin), "least_conn": len(least_conn),
            "weighted": len(weighted), "total_rps": rps, "healthy": True}
