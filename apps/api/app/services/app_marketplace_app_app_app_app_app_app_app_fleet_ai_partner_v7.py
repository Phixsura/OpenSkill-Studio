"""Fleet AI Partner v7 — track AI platform partner ecosystem."""
from __future__ import annotations
def fleet_ai_partner_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    partners = sum(s.get("partners", 0) for s in systems)
    integrations = sum(s.get("integrations", 0) for s in systems)
    revenue_share = round(sum(s.get("revenue_pct", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "partners": partners,
            "integrations": integrations, "revenue_share": revenue_share, "thriving": partners > 100}
