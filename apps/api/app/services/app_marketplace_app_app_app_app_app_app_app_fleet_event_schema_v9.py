"""Fleet Event Schema v9 — track event schema registry and evolution."""
from __future__ import annotations
def fleet_event_schema_v9(schemas: list[dict]) -> dict:
    compatible = [s for s in schemas if s.get("compatible")]
    breaking = [s for s in schemas if s.get("breaking")]
    versions = sum(s.get("versions", 1) for s in schemas)
    return {"schemas": len(schemas), "compatible": len(compatible), "breaking": len(breaking),
            "total_versions": versions, "healthy": len(breaking) == 0}
