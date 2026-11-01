"""Fleet AI Observability v8 — track ultimate three-pillar observability."""
from __future__ import annotations
def fleet_ai_observability_v8(stacks: list[dict]) -> dict:
    active = [s for s in stacks if s.get("active", True)]
    metrics = sum(s.get("metrics_24h", 0) for s in stacks)
    traces = sum(s.get("traces_24h", 0) for s in stacks)
    logs = sum(s.get("logs_24h", 0) for s in stacks)
    return {"stacks": len(stacks), "active": len(active), "metrics": metrics,
            "traces": traces, "logs": logs, "complete": metrics > 0 and traces > 0 and logs > 0}
