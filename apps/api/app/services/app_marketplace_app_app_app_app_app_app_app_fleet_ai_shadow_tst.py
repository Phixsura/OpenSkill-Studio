"""Fleet AI Shadow Testing — track shadow/mirror traffic for AI models."""
from __future__ import annotations
def fleet_ai_shadow_test(shadows: list[dict]) -> dict:
    active = [s for s in shadows if s.get("active", True)]
    mirrored_24h = sum(s.get("mirrored_24h", 0) for s in shadows)
    divergence_pct = round(sum(s.get("divergence_pct", 0) for s in shadows) / max(len(shadows), 1), 2)
    return {"shadows": len(shadows), "active": len(active), "mirrored_24h": mirrored_24h,
            "divergence_pct": divergence_pct, "consistent": divergence_pct < 5}
