"""Fleet AI Tracing — track distributed tracing for AI inference chains."""
from __future__ import annotations
def fleet_ai_tracing(tracers: list[dict]) -> dict:
    active = [t for t in tracers if t.get("active", True)]
    traces_24h = sum(t.get("traces_24h", 0) for t in tracers)
    spans_24h = sum(t.get("spans_24h", 0) for t in tracers)
    avg_depth = round(sum(t.get("avg_depth", 0) for t in tracers) / max(len(tracers), 1), 1)
    return {"tracers": len(tracers), "active": len(active), "traces_24h": traces_24h,
            "spans_24h": spans_24h, "avg_depth": avg_depth, "deep": avg_depth > 5}
