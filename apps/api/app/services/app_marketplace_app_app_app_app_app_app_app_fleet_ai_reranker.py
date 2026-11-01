"""Fleet AI Reranker — track search result reranking with AI models."""
from __future__ import annotations
def fleet_ai_reranker(rerankers: list[dict]) -> dict:
    active = [r for r in rerankers if r.get("active", True)]
    queries_24h = sum(r.get("queries_24h", 0) for r in rerankers)
    ndcg_improvement = round(sum(r.get("ndcg_boost", 0) for r in rerankers) / max(len(rerankers), 1), 2)
    latency_ms = round(sum(r.get("latency_ms", 0) for r in rerankers) / max(len(rerankers), 1), 1)
    return {"rerankers": len(rerankers), "active": len(active), "queries_24h": queries_24h,
            "ndcg_boost": ndcg_improvement, "latency_ms": latency_ms, "improving": ndcg_improvement > 0.05}
