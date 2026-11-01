"""Fleet schema registry — track schema compatibility."""
from __future__ import annotations
def fleet_schema_registry(schemas: list[dict]) -> dict:
    compatible = [s for s in schemas if s.get("compatible", True)]
    breaking = [s for s in schemas if not s.get("compatible", True)]
    return {"total": len(schemas), "compatible": len(compatible),
            "breaking": len(breaking), "safe": len(breaking) == 0}
