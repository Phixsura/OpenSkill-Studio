"""Fleet Edge Routing v9 — track edge network traffic routing."""
from __future__ import annotations
def fleet_edge_routing_v9(rules: list[dict]) -> dict:
    active = [r for r in rules if r.get("active")]
    geo_rules = [r for r in rules if r.get("type") == "geo"]
    latency_rules = [r for r in rules if r.get("type") == "latency"]
    rps = sum(r.get("rps", 0) for r in rules)
    return {"rules": len(rules), "active": len(active), "geo": len(geo_rules),
            "latency_based": len(latency_rules), "total_rps": rps, "healthy": len(active) == len(rules)}
