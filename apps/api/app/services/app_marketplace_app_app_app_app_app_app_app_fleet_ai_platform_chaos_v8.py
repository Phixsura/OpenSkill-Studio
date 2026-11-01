"""Fleet AI Chaos v8 — track ultimate chaos engineering."""
from __future__ import annotations
def fleet_ai_chaos_v8(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    experiments = sum(s.get("experiments_24h", 0) for s in systems)
    recovery = round(sum(s.get("recovery_s", 0) for s in systems) / max(len(systems), 1), 1)
    blast = round(sum(s.get("blast_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "experiments": experiments,
            "recovery_s": recovery, "blast_pct": blast, "resilient": recovery < 30}
