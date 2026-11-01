"""Fleet AI Cache Layer — track semantic and KV caching for AI responses."""
from __future__ import annotations
def fleet_ai_cache_layer(caches: list[dict]) -> dict:
    active = [c for c in caches if c.get("active", True)]
    hit_rate = round(sum(c.get("hit_rate", 0) for c in caches) / max(len(caches), 1), 1)
    entries = sum(c.get("entries", 0) for c in caches)
    saved_tokens = sum(c.get("saved_tokens", 0) for c in caches)
    return {"caches": len(caches), "active": len(active), "hit_rate": hit_rate,
            "entries": entries, "saved_tokens": saved_tokens, "efficient": hit_rate > 50}
