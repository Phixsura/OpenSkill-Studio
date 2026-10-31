"""Fleet AI Response Cache v2 — track semantic AI response caching."""
from __future__ import annotations
def fleet_ai_response_cache_v2(caches: list[dict]) -> dict:
    active = [c for c in caches if c.get("active", True)]
    entries = sum(c.get("entries", 0) for c in caches)
    hit_rate = round(sum(c.get("hit_rate", 0) for c in caches) / max(len(caches), 1), 1)
    tokens_saved = sum(c.get("tokens_saved", 0) for c in caches)
    return {"caches": len(caches), "active": len(active), "entries": entries,
            "hit_rate": hit_rate, "tokens_saved": tokens_saved, "effective": hit_rate > 50}
