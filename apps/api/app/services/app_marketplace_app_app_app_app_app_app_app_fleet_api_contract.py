"""Fleet API contract validator — validate API contracts."""
from __future__ import annotations
def fleet_api_contract_validator(endpoints: list[dict]) -> dict:
    valid = [e for e in endpoints if e.get("schema_valid", True)]
    invalid = len(endpoints) - len(valid)
    return {"total": len(endpoints), "valid": len(valid), "invalid": invalid,
            "all_valid": invalid == 0}
