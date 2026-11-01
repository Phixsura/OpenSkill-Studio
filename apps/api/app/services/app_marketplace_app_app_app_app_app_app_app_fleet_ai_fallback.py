"""Fleet AI Fallback — track model fallback chain health."""
from __future__ import annotations
def fleet_ai_fallback(chains: list[dict]) -> dict:
    active = [c for c in chains if c.get("active", True)]
    fallbacks_triggered = sum(c.get("fallbacks_24h", 0) for c in chains)
    primary_success = round(sum(c.get("primary_success_pct", 100) for c in chains) / max(len(chains), 1), 1)
    return {"chains": len(chains), "active": len(active), "fallbacks_24h": fallbacks_triggered,
            "primary_success_pct": primary_success, "resilient": len(active) == len(chains)}
