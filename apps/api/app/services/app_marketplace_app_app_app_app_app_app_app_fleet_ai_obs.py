"""Fleet AI Observability — track LLM traces and metrics."""
from __future__ import annotations
def fleet_ai_observability(instances: list[dict]) -> dict:
    active = [i for i in instances if i.get("active", True)]
    traces_24h = sum(i.get("traces_24h", 0) for i in instances)
    spans_24h = sum(i.get("spans_24h", 0) for i in instances)
    return {"instances": len(instances), "active": len(active), "traces_24h": traces_24h,
            "spans_24h": spans_24h, "comprehensive": traces_24h > 0}
