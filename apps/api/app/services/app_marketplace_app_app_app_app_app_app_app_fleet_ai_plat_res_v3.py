"""Fleet AI Platform Resilience v3 — track ultimate platform fault tolerance."""
from __future__ import annotations
def fleet_ai_platform_resilience_v3(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    blast_radius = round(sum(s.get("blast_radius_pct", 0) for s in systems) / max(len(systems), 1), 1)
    recovery_time_s = round(sum(s.get("recovery_s", 0) for s in systems) / max(len(systems), 1), 1)
    chaos_score = round(sum(s.get("chaos_score", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "blast_radius": blast_radius,
            "recovery_s": recovery_time_s, "chaos_score": chaos_score, "resilient": chaos_score > 90}
