"""Fleet AI Observability v4 — track three pillars of observability at scale."""
from __future__ import annotations
def fleet_ai_observability_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    metrics = sum(s.get("metrics", 0) for s in systems)
    traces = sum(s.get("traces", 0) for s in systems)
    logs = sum(s.get("logs", 0) for s in systems)
    cardinality = sum(s.get("cardinality", 0) for s in systems)
    return {"systems": len(systems), "active": len(active), "metrics": metrics,
            "traces": traces, "logs": logs, "cardinality": cardinality, "complete": metrics > 0 and traces > 0 and logs > 0}
