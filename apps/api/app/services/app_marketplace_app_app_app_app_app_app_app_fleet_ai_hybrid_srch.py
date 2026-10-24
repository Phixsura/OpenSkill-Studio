"""Fleet AI Hybrid Search — track combined keyword + semantic search."""
from __future__ import annotations
def fleet_ai_hybrid_search(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    queries_24h = sum(e.get("queries_24h", 0) for e in engines)
    mrr = round(sum(e.get("mrr", 0) for e in engines) / max(len(engines), 1), 3)
    docs = sum(e.get("docs", 0) for e in engines)
    return {"engines": len(engines), "active": len(active), "queries_24h": queries_24h,
            "mrr": mrr, "docs": docs, "accurate": mrr > 0.85}
