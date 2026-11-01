"""Fleet Request Validation v9 — track API request schema validation."""
from __future__ import annotations
def fleet_request_validation_v9(validators: list[dict]) -> dict:
    active = [v for v in validators if v.get("active")]
    rejected = sum(v.get("rejected_today", 0) for v in validators)
    total_validated = sum(v.get("validated_today", 0) for v in validators)
    return {"validators": len(validators), "active": len(active), "rejected_today": rejected,
            "validated_today": total_validated, "healthy": True}
