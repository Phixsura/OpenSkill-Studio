"""Fleet AI Search — track semantic search platform."""
from __future__ import annotations
def fleet_ai_search(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    queries_24h = sum(e.get("queries_24h", 0) for e in engines)
    relevance_score = round(sum(e.get("relevance_score", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "queries_24h": queries_24h,
            "relevance_score": relevance_score, "high_quality": relevance_score >= 90}
