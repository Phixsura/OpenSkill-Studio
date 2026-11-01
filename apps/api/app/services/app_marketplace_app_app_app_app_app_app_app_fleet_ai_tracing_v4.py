"""Fleet AI Tracing v4 — track distributed tracing at platform scale."""
from __future__ import annotations
def fleet_ai_tracing_v4(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    traces_24h = sum(s.get("traces_24h", 0) for s in systems)
    spans_24h = sum(s.get("spans_24h", 0) for s in systems)
    sampling_pct = round(sum(s.get("sampling_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "traces_24h": traces_24h,
            "spans_24h": spans_24h, "sampling_pct": sampling_pct, "tracing": traces_24h > 0}
