"""Fleet API Fallback v9 — track API fallback and degradation strategies."""
from __future__ import annotations
def fleet_api_fallback_v9(fallbacks: list[dict]) -> dict:
    configured = [f for f in fallbacks if f.get("configured")]
    triggered = sum(f.get("triggered_today", 0) for f in fallbacks)
    cached_responses = sum(f.get("cached_responses", 0) for f in fallbacks)
    return {"fallbacks": len(fallbacks), "configured": len(configured), "triggered_today": triggered,
            "cached_responses": cached_responses, "healthy": len(configured) == len(fallbacks)}
