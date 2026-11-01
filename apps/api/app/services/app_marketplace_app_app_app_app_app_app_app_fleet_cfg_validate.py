"""Fleet config validation — validate configs before deploy."""
from __future__ import annotations
def fleet_config_validation(configs: list[dict]) -> dict:
    valid = [c for c in configs if c.get("valid", True)]
    invalid = len(configs) - len(valid)
    return {"total": len(configs), "valid": len(valid), "invalid": invalid,
            "safe_to_deploy": invalid == 0}
