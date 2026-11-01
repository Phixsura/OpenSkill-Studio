"""Fleet AI Semantic Search — track vector-powered semantic retrieval."""
from __future__ import annotations
def fleet_ai_semantic_search(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    queries_24h = sum(e.get("queries_24h", 0) for e in engines)
    docs_indexed = sum(e.get("docs_indexed", 0) for e in engines)
    mrr = round(sum(e.get("mrr", 0) for e in engines) / max(len(engines), 1), 3)
    return {"engines": len(engines), "active": len(active), "queries_24h": queries_24h,
            "docs_indexed": docs_indexed, "mrr": mrr, "accurate": mrr > 0.8}
