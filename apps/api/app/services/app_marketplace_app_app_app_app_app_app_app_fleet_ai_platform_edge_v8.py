"""Fleet AI Edge v8 — track ultimate edge AI deployment."""
from __future__ import annotations
def fleet_ai_edge_v8(edges: list[dict]) -> dict:
    active = [e for e in edges if e.get("active", True)]
    locations = sum(e.get("locations", 0) for e in edges)
    requests = sum(e.get("requests_24h", 0) for e in edges)
    p50 = round(sum(e.get("p50_ms", 0) for e in edges) / max(len(edges), 1), 1)
    return {"edges": len(edges), "active": len(active), "locations": locations,
            "requests": requests, "p50": p50, "ultra_low": p50 < 5}
