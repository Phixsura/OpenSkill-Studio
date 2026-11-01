"""Fleet AI Model Cache v3 — track advanced model weight caching."""
from __future__ import annotations
def fleet_ai_model_cache_v3(caches: list[dict]) -> dict:
    active = [c for c in caches if c.get("active", True)]
    models_cached = sum(c.get("models", 0) for c in caches)
    hit_rate = round(sum(c.get("hit_rate", 0) for c in caches) / max(len(caches), 1), 1)
    memory_gb = round(sum(c.get("memory_gb", 0) for c in caches), 1)
    return {"caches": len(caches), "active": len(active), "models": models_cached,
            "hit_rate": hit_rate, "memory_gb": memory_gb, "warm": hit_rate > 80}
