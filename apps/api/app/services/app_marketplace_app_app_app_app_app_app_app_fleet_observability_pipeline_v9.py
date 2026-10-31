"""Fleet Observability Pipeline v9 — unified metrics+logs+traces pipeline."""
from __future__ import annotations
def fleet_observability_pipeline_v9(stages: list[dict]) -> dict:
    active = [s for s in stages if s.get("active")]
    throughput = sum(s.get("events_per_sec", 0) for s in stages)
    dropped = sum(s.get("dropped", 0) for s in stages)
    return {"stages": len(stages), "active": len(active), "throughput_eps": throughput,
            "dropped": dropped, "healthy": dropped == 0}
