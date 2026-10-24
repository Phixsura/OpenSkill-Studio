"""Fleet AI Telemetry — track LLM application telemetry."""
from __future__ import annotations
def fleet_ai_telemetry(collectors: list[dict]) -> dict:
    active = [c for c in collectors if c.get("active", True)]
    spans_24h = sum(c.get("spans_24h", 0) for c in collectors)
    tokens_tracked = sum(c.get("tokens_tracked_24h", 0) for c in collectors)
    cost_tracked = sum(c.get("cost_tracked_24h", 0) for c in collectors)
    return {"collectors": len(collectors), "active": len(active), "spans_24h": spans_24h,
            "tokens_tracked": tokens_tracked, "cost_tracked": round(cost_tracked, 2)}
