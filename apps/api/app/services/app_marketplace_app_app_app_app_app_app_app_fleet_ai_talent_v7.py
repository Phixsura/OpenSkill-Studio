"""Fleet AI Talent v7 — track AI engineering talent management."""
from __future__ import annotations
def fleet_ai_talent_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    engineers = sum(s.get("engineers", 0) for s in systems)
    hiring = sum(s.get("hiring", 0) for s in systems)
    retention = round(sum(s.get("retention_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "engineers": engineers,
            "hiring": hiring, "retention": retention, "strong": retention > 90}
