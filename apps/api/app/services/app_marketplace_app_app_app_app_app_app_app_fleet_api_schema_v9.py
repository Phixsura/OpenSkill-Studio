"""Fleet API Schema v9 — track API schema evolution and validation."""
from __future__ import annotations
def fleet_api_schema_v9(schemas: list[dict]) -> dict:
    valid = [s for s in schemas if s.get("valid")]
    versions = sum(s.get("versions", 1) for s in schemas)
    breaking = [s for s in schemas if s.get("breaking_change")]
    return {"schemas": len(schemas), "valid": len(valid), "total_versions": versions,
            "breaking_changes": len(breaking), "healthy": len(breaking) == 0}
