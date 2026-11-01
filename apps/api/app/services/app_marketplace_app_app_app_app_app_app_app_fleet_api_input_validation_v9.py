"""Fleet API Input Validation v9 — track comprehensive input validation."""
from __future__ import annotations
def fleet_api_input_validation_v9(endpoints: list[dict]) -> dict:
    validated = [e for e in endpoints if e.get("validation_enabled")]
    rejected = sum(e.get("rejected_today", 0) for e in endpoints)
    schemas = len({e.get("schema") for e in endpoints if e.get("schema")})
    return {"endpoints": len(endpoints), "validated": len(validated), "rejected_today": rejected,
            "schemas": schemas, "healthy": len(validated) == len(endpoints)}
