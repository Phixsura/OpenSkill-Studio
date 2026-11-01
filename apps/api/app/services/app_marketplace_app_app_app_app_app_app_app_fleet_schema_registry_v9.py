"""Fleet Schema Registry v9 — track API schema versions and compatibility."""
from __future__ import annotations
def fleet_schema_registry_v9(schemas: list[dict]) -> dict:
    compatible = [s for s in schemas if s.get("compatible", True)]
    versions = sum(s.get("versions", 1) for s in schemas)
    return {"total_schemas": len(schemas), "compatible": len(compatible), "total_versions": versions,
            "breaking_changes": len(schemas) - len(compatible),
            "healthy": len(compatible) == len(schemas)}
