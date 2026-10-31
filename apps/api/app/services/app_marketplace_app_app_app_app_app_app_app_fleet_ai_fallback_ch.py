"""Fleet AI Fallback Chain — track multi-model fallback routing."""
from __future__ import annotations
def fleet_ai_fallback_chain(chains: list[dict]) -> dict:
    active = [c for c in chains if c.get("active", True)]
    fallbacks_24h = sum(c.get("fallbacks_24h", 0) for c in chains)
    models_in_chain = max((c.get("models", 0) for c in chains), default=0)
    success_rate = round(sum(c.get("success_pct", 0) for c in chains) / max(len(chains), 1), 1)
    return {"chains": len(chains), "active": len(active), "fallbacks_24h": fallbacks_24h,
            "models": models_in_chain, "success_rate": success_rate, "resilient": success_rate > 99}
