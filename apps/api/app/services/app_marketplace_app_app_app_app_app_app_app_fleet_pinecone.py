"""Fleet Pinecone — track vector database index health."""
from __future__ import annotations
def fleet_pinecone_status(indexes: list[dict]) -> dict:
    ready = [i for i in indexes if i.get("status") == "Ready"]
    total_vectors = sum(i.get("vector_count", 0) for i in indexes)
    total_qps = sum(i.get("qps", 0) for i in indexes)
    return {"indexes": len(indexes), "ready": len(ready), "vectors": total_vectors,
            "qps": total_qps, "all_ready": len(ready) == len(indexes)}
