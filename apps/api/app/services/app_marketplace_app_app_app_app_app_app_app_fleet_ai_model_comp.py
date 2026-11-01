"""Fleet AI Model Compliance — track model regulatory compliance checks."""
from __future__ import annotations
def fleet_ai_model_compliance(checkers: list[dict]) -> dict:
    active = [c for c in checkers if c.get("active", True)]
    models_checked = sum(c.get("models", 0) for c in checkers)
    passed = sum(c.get("passed", 0) for c in checkers)
    failed = sum(c.get("failed", 0) for c in checkers)
    frameworks = sum(c.get("frameworks", 0) for c in checkers)
    return {"checkers": len(checkers), "active": len(active), "models": models_checked,
            "passed": passed, "failed": failed, "frameworks": frameworks, "compliant": failed == 0}
