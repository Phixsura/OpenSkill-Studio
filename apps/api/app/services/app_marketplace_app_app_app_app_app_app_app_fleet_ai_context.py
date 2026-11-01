"""Fleet AI Context Window — track context utilization."""
from __future__ import annotations
def fleet_ai_context(services: list[dict]) -> dict:
    active = [s for s in services if s.get("active", True)]
    avg_utilization = round(sum(s.get("ctx_utilization_pct", 0) for s in services) / max(len(services), 1), 1)
    truncations = sum(s.get("truncations_24h", 0) for s in services)
    return {"services": len(services), "active": len(active), "avg_utilization_pct": avg_utilization,
            "truncations_24h": truncations, "efficient": avg_utilization < 80}
