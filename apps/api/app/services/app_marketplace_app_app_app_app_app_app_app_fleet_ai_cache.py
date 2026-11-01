"""Fleet AI Inference Cache — track semantic caching for LLMs."""
from __future__ import annotations
def fleet_ai_cache(caches: list[dict]) -> dict:
    active = [c for c in caches if c.get("active", True)]
    hit_rate = round(sum(c.get("hit_rate_pct", 0) for c in caches) / max(len(caches), 1), 1)
    tokens_saved = sum(c.get("tokens_saved_24h", 0) for c in caches)
    cost_saved = sum(c.get("cost_saved_24h", 0) for c in caches)
    return {"caches": len(caches), "active": len(active), "hit_rate": hit_rate,
            "tokens_saved": tokens_saved, "cost_saved": round(cost_saved, 2)}
