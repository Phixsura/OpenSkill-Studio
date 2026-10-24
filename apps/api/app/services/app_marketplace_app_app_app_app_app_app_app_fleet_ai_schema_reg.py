"""Fleet AI Schema Registry — track AI data schema versioning."""
from __future__ import annotations
def fleet_ai_schema_registry(registries: list[dict]) -> dict:
    active = [r for r in registries if r.get("active", True)]
    schemas = sum(r.get("schemas", 0) for r in registries)
    versions = sum(r.get("versions", 0) for r in registries)
    validations_24h = sum(r.get("validations_24h", 0) for r in registries)
    return {"registries": len(registries), "active": len(active), "schemas": schemas,
            "versions": versions, "validations_24h": validations_24h, "governed": schemas > 0}
