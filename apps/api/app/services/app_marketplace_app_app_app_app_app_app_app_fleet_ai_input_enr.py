"""Fleet AI Input Enricher — track AI request context augmentation."""
from __future__ import annotations
def fleet_ai_input_enricher(enrichers: list[dict]) -> dict:
    active = [e for e in enrichers if e.get("active", True)]
    enriched_24h = sum(e.get("enriched_24h", 0) for e in enrichers)
    sources = sum(e.get("sources", 0) for e in enrichers)
    avg_added_tokens = round(sum(e.get("added_tokens", 0) for e in enrichers) / max(len(enrichers), 1))
    return {"enrichers": len(enrichers), "active": len(active), "enriched_24h": enriched_24h,
            "sources": sources, "added_tokens": avg_added_tokens, "enriching": sources > 0}
