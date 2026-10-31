"""Fleet AI Chunker — track document chunking for RAG pipelines."""
from __future__ import annotations
def fleet_ai_chunker(chunkers: list[dict]) -> dict:
    active = [c for c in chunkers if c.get("active", True)]
    docs_24h = sum(c.get("docs_24h", 0) for c in chunkers)
    chunks_created = sum(c.get("chunks", 0) for c in chunkers)
    avg_size = round(sum(c.get("avg_tokens", 0) for c in chunkers) / max(len(chunkers), 1))
    return {"chunkers": len(chunkers), "active": len(active), "docs_24h": docs_24h,
            "chunks": chunks_created, "avg_tokens": avg_size, "processing": docs_24h > 0}
