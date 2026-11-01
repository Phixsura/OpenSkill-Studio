"""Fleet Chroma — track Chroma embedding database health."""
from __future__ import annotations
def fleet_chroma_status(collections: list[dict]) -> dict:
    total_docs = sum(c.get("documents", 0) for c in collections)
    total_embeddings = sum(c.get("embeddings", 0) for c in collections)
    return {"collections": len(collections), "documents": total_docs,
            "embeddings": total_embeddings, "synced": total_docs == total_embeddings}
