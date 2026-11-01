"""Fleet RAG — track retrieval-augmented generation pipelines."""
from __future__ import annotations
def fleet_rag_status(pipelines: list[dict]) -> dict:
    active = [p for p in pipelines if p.get("active", True)]
    queries_24h = sum(p.get("queries_24h", 0) for p in pipelines)
    docs_indexed = sum(p.get("docs_indexed", 0) for p in pipelines)
    return {"pipelines": len(pipelines), "active": len(active), "queries_24h": queries_24h,
            "docs_indexed": docs_indexed, "all_active": len(active) == len(pipelines)}
