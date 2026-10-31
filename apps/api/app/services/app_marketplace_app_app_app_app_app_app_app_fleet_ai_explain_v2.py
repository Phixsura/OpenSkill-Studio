"""Fleet AI Model Explainer v2 — track next-gen model interpretability."""
from __future__ import annotations
def fleet_ai_explainer_v2(explainers: list[dict]) -> dict:
    active = [e for e in explainers if e.get("active", True)]
    explanations_24h = sum(e.get("explanations_24h", 0) for e in explainers)
    methods = set()
    for e in explainers:
        methods.update(e.get("methods", []))
    user_satisfaction = round(sum(e.get("satisfaction", 0) for e in explainers) / max(len(explainers), 1), 1)
    return {"explainers": len(explainers), "active": len(active), "explanations_24h": explanations_24h,
            "methods": len(methods), "satisfaction": user_satisfaction, "clear": user_satisfaction > 80}
