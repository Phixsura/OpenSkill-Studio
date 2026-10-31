"""Fleet AI Sampling — track intelligent request sampling for observability."""
from __future__ import annotations
def fleet_ai_sampling(samplers: list[dict]) -> dict:
    active = [s for s in samplers if s.get("active", True)]
    sample_rate = round(sum(s.get("rate_pct", 0) for s in samplers) / max(len(samplers), 1), 1)
    sampled_24h = sum(s.get("sampled_24h", 0) for s in samplers)
    storage_saved_pct = round(sum(s.get("saved_pct", 0) for s in samplers) / max(len(samplers), 1), 1)
    return {"samplers": len(samplers), "active": len(active), "rate_pct": sample_rate,
            "sampled_24h": sampled_24h, "saved_pct": storage_saved_pct, "efficient": storage_saved_pct > 50}
