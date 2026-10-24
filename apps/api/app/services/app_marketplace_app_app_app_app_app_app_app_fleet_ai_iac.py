"""Fleet AI Infrastructure as Code — track AI infra provisioning automation."""
from __future__ import annotations
def fleet_ai_iac(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    resources_managed = sum(s.get("resources", 0) for s in systems)
    applies_24h = sum(s.get("applies_24h", 0) for s in systems)
    drift_free_pct = round(sum(s.get("drift_free_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "resources": resources_managed,
            "applies_24h": applies_24h, "drift_free_pct": drift_free_pct, "automated": drift_free_pct > 95}
