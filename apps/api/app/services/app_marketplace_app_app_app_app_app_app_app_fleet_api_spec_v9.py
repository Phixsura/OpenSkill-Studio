"""Fleet API Spec v9 — track OpenAPI specification management."""
from __future__ import annotations
def fleet_api_spec_v9(specs: list[dict]) -> dict:
    valid = [s for s in specs if s.get("valid")]
    auto_generated = [s for s in specs if s.get("auto_generated")]
    versions = sum(s.get("versions", 1) for s in specs)
    return {"specs": len(specs), "valid": len(valid), "auto_generated": len(auto_generated),
            "total_versions": versions, "healthy": len(valid) == len(specs)}
