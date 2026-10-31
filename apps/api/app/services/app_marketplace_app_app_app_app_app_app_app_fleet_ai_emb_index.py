"""Fleet AI Embedding Index — track vector embedding indexing and search."""
from __future__ import annotations
def fleet_ai_embedding_index(indexes: list[dict]) -> dict:
    active = [i for i in indexes if i.get("active", True)]
    vectors = sum(i.get("vectors", 0) for i in indexes)
    dims = max((i.get("dims", 0) for i in indexes), default=0)
    searches_24h = sum(i.get("searches_24h", 0) for i in indexes)
    p99_ms = round(sum(i.get("p99_ms", 0) for i in indexes) / max(len(indexes), 1), 1)
    return {"indexes": len(indexes), "active": len(active), "vectors": vectors,
            "dims": dims, "searches_24h": searches_24h, "p99_ms": p99_ms, "fast": p99_ms < 50}
