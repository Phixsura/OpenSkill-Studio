"""Fleet AI Chaos Engineering v7 — track ultimate resilience testing."""
from __future__ import annotations
def fleet_ai_chaos_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    experiments_24h = sum(s.get("experiments", 0) for s in systems)
    blast_radius = round(sum(s.get("blast_pct", 0) for s in systems) / max(len(systems), 1), 1)
    recovery_s = round(sum(s.get("recovery_s", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "experiments": experiments_24h,
            "blast_pct": blast_radius, "recovery_s": recovery_s, "resilient": recovery_s < 30}
