"""Fleet AI Inference Cache — track semantic response caching."""
from __future__ import annotations
def fleet_ai_inference_cache(caches: list[dict]) -> dict:
    active = [c for c in caches if c.get("active", True)]
    entries = sum(c.get("entries", 0) for c in caches)
    hit_rate = round(sum(c.get("hit_rate", 0) for c in caches) / max(len(caches), 1), 1)
    cost_saved_24h = round(sum(c.get("cost_saved", 0) for c in caches), 2)
    return {"caches": len(caches), "active": len(active), "entries": entries,
            "hit_rate": hit_rate, "cost_saved": cost_saved_24h, "valuable": cost_saved_24h > 100}
