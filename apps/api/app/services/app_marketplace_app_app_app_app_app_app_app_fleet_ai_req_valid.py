"""Fleet AI Request Validator — track AI API request schema validation."""
from __future__ import annotations
def fleet_ai_request_validator(validators: list[dict]) -> dict:
    active = [v for v in validators if v.get("active", True)]
    validated_24h = sum(v.get("validated_24h", 0) for v in validators)
    rejected = sum(v.get("rejected", 0) for v in validators)
    schemas = sum(v.get("schemas", 0) for v in validators)
    return {"validators": len(validators), "active": len(active), "validated_24h": validated_24h,
            "rejected": rejected, "schemas": schemas, "strict": schemas > 0}
