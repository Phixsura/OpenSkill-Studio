"""Fleet AI Edge Inference — track AI inference at edge locations."""
from __future__ import annotations
def fleet_ai_edge_inference(edges: list[dict]) -> dict:
    active = [e for e in edges if e.get("active", True)]
    locations = len(set(e.get("location", "") for e in edges))
    requests_24h = sum(e.get("requests_24h", 0) for e in edges)
    p50_ms = round(sum(e.get("p50_ms", 0) for e in edges) / max(len(edges), 1), 1)
    return {"edges": len(edges), "active": len(active), "locations": locations,
            "requests_24h": requests_24h, "p50_ms": p50_ms, "fast": p50_ms < 20}
