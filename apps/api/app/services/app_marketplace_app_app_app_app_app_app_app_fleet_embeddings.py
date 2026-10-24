"""Fleet Embeddings — track vector embedding service."""
from __future__ import annotations
def fleet_embeddings_status(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    embeddings_24h = sum(s.get("embeddings_24h", 0) for s in services)
    dimensions = max((s.get("dimensions", 0) for s in services), default=0)
    return {"services": len(services), "active": len(active), "embeddings_24h": embeddings_24h,
            "max_dimensions": dimensions, "all_active": len(active) == len(services)}
