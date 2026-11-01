"""Fleet AI Knowledge Base — track AI-powered knowledge management systems."""
from __future__ import annotations
def fleet_ai_knowledge_base(bases: list[dict]) -> dict:
    active = [b for b in bases if b.get("active", True)]
    articles = sum(b.get("articles", 0) for b in bases)
    searches_24h = sum(b.get("searches_24h", 0) for b in bases)
    helpful_pct = round(sum(b.get("helpful_pct", 0) for b in bases) / max(len(bases), 1), 1)
    return {"bases": len(bases), "active": len(active), "articles": articles,
            "searches_24h": searches_24h, "helpful_pct": helpful_pct, "useful": helpful_pct > 80}
