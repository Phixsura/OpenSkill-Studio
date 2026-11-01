"""Fleet AI Model Signature — track model input/output schema validation."""
from __future__ import annotations
def fleet_ai_model_signature(validators: list[dict]) -> dict:
    active = [v for v in validators if v.get("active", True)]
    models_validated = sum(v.get("models", 0) for v in validators)
    schemas = sum(v.get("schemas", 0) for v in validators)
    violations_24h = sum(v.get("violations_24h", 0) for v in validators)
    return {"validators": len(validators), "active": len(active), "models": models_validated,
            "schemas": schemas, "violations_24h": violations_24h, "valid": violations_24h == 0}
