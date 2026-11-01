"""Fleet AI Risk Management v7 — track AI platform risk assessment."""
from __future__ import annotations
def fleet_ai_risk_mgmt_v7(systems: list[dict]) -> dict:
    active = [s for s in systems if s.get("active", True)]
    risks = sum(s.get("risks", 0) for s in systems)
    mitigated = sum(s.get("mitigated", 0) for s in systems)
    score = round(sum(s.get("score", 0) for s in systems) / max(len(systems), 1), 1)
    return {"systems": len(systems), "active": len(active), "risks": risks,
            "mitigated": mitigated, "score": score, "managed": mitigated >= risks}
