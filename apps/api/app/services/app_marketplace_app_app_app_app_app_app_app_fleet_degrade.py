"""Fleet graceful degradation — track fallback activation."""
from __future__ import annotations
def fleet_graceful_degradation(services: list[dict]) -> dict:
    degraded = [s for s in services if s.get("fallback_active", False)]
    with_fallback = [s for s in services if s.get("has_fallback", False)]
    return {"total": len(services), "degraded": len(degraded), "with_fallback": len(with_fallback),
            "without_fallback": len(services) - len(with_fallback), "all_protected": len(with_fallback) == len(services)}
