"""Fleet AI Explainability — track model interpretability and XAI."""
from __future__ import annotations
def fleet_ai_explainability(engines: list[dict]) -> dict:
    active = [e for e in engines if e.get("active", True)]
    explanations_24h = sum(e.get("explanations_24h", 0) for e in engines)
    methods = set()
    for e in engines:
        methods.update(e.get("methods", []))
    coverage = round(sum(e.get("coverage", 0) for e in engines) / max(len(engines), 1), 1)
    return {"engines": len(engines), "active": len(active), "explanations_24h": explanations_24h,
            "methods": sorted(methods), "coverage": coverage, "transparent": coverage > 80}
