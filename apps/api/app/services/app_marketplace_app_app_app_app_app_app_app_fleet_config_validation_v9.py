"""Fleet Config Validation v9 — track configuration schema validation."""
from __future__ import annotations
def fleet_config_validation_v9(configs: list[dict]) -> dict:
    valid = [c for c in configs if c.get("valid")]
    invalid = [c for c in configs if not c.get("valid")]
    schemas = len({c.get("schema") for c in configs if c.get("schema")})
    return {"configs": len(configs), "valid": len(valid), "invalid": len(invalid),
            "schemas": schemas, "healthy": len(invalid) == 0}
