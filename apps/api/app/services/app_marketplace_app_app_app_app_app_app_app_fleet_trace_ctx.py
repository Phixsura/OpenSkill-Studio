"""Fleet trace context — track context propagation coverage."""
from __future__ import annotations
def fleet_trace_context(services: list[dict]) -> dict:
    propagating = [s for s in services if s.get("propagates_context", False)]
    pct = round(len(propagating) / max(len(services), 1) * 100, 1)
    return {"total": len(services), "propagating": len(propagating),
            "missing": len(services) - len(propagating), "coverage_pct": pct, "complete": pct == 100}
