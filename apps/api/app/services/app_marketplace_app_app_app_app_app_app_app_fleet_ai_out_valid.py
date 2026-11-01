"""Fleet AI Output Validator — track AI response validation and filtering."""
from __future__ import annotations
def fleet_ai_output_validator(validators: list[dict]) -> dict:
    active = [v for v in validators if v.get("active", True)]
    validated_24h = sum(v.get("validated_24h", 0) for v in validators)
    rejected_24h = sum(v.get("rejected_24h", 0) for v in validators)
    rules = sum(v.get("rules", 0) for v in validators)
    return {"validators": len(validators), "active": len(active), "validated_24h": validated_24h,
            "rejected_24h": rejected_24h, "rules": rules, "enforcing": rules > 0}
