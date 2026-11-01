"""Fleet AI Embeddings — track vector embedding generation pipelines."""
from __future__ import annotations
def fleet_ai_embeddings(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    vectors_24h = sum(p.get("vectors_24h", 0) for p in pipelines)
    dims = max((p.get("dimensions", 0) for p in pipelines), default=0)
    return {"pipelines": len(pipelines), "active": len(active), "vectors_24h": vectors_24h,
            "max_dimensions": dims, "healthy": len(active) == len(pipelines)}
