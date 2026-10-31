"""Fleet AI Model Governance v2 — track model lifecycle governance."""
from __future__ import annotations
def fleet_ai_model_governance_v2(frameworks: list[dict]) -> dict:
    active = [f for f in frameworks if f.get("active", True)]
    models = sum(f.get("models", 0) for f in frameworks)
    policies = sum(f.get("policies", 0) for f in frameworks)
    compliance = round(sum(f.get("compliance_pct", 0) for f in frameworks) / max(len(frameworks), 1), 1)
    approvals_24h = sum(f.get("approvals_24h", 0) for f in frameworks)
    return {"frameworks": len(frameworks), "active": len(active), "models": models,
            "policies": policies, "compliance": compliance, "approvals": approvals_24h, "governed": compliance > 95}
