"""Fleet AI Customer v7 — track AI platform customer success."""
from __future__ import annotations
def fleet_ai_customer_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    customers = sum(s.get("customers", 0) for s in systems)
    csat = round(sum(s.get("csat", 0) for s in systems) / max(len(systems), 1), 1)
    nps = round(sum(s.get("nps", 0) for s in systems) / max(len(systems), 1))
    churn = round(sum(s.get("churn_pct", 0) for s in systems) / max(len(systems), 1), 2)
    return {"systems": len(systems), "active": len(active), "customers": customers,
            "csat": csat, "nps": nps, "churn": churn, "loyal": nps > 50 and churn < 5}
