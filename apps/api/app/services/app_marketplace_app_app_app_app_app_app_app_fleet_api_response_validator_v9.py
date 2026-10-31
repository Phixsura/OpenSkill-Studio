"""Fleet API Response Validator v9 — track response schema validation."""
from __future__ import annotations
def fleet_api_response_validator_v9(validators: list[dict]) -> dict:
    active = [v for v in validators if v.get("active")]
    violations = sum(v.get("violations_today", 0) for v in validators)
    validated = sum(v.get("validated_today", 0) for v in validators)
    return {"validators": len(validators), "active": len(active), "violations_today": violations,
            "validated_today": validated, "healthy": violations == 0}
