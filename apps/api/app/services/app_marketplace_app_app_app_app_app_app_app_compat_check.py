"""API backward compatibility checker — detect breaking API changes."""
from __future__ import annotations


def check_compatibility(old_schema: dict, new_schema: dict) -> dict:
    breaking = []
    warnings = []
    old_fields = set(old_schema.get("fields", {}).keys())
    new_fields = set(new_schema.get("fields", {}).keys())
    # Removed fields are breaking
    for f in old_fields - new_fields:
        breaking.append({"type": "field_removed", "field": f})
    # Type changes are breaking
    for f in old_fields & new_fields:
        old_type = old_schema["fields"][f]
        new_type = new_schema["fields"][f]
        if old_type != new_type:
            breaking.append({"type": "type_changed", "field": f, "old": old_type, "new": new_type})
    # Added required fields are breaking
    old_required = set(old_schema.get("required", []))
    new_required = set(new_schema.get("required", []))
    for f in new_required - old_required:
        if f not in old_fields:
            breaking.append({"type": "new_required_field", "field": f})
    # Added optional fields are fine
    for f in new_fields - old_fields:
        if f not in new_required:
            warnings.append({"type": "field_added", "field": f})
    compatible = len(breaking) == 0
    return {"compatible": compatible, "breaking": breaking, "warnings": warnings,
            "total_issues": len(breaking) + len(warnings)}


def version_compatibility_matrix(versions: list[dict]) -> dict:
    results = []
    for i in range(len(versions) - 1):
        r = check_compatibility(versions[i]["schema"], versions[i+1]["schema"])
        results.append({"from": versions[i]["version"], "to": versions[i+1]["version"],
                         "compatible": r["compatible"], "breaking": len(r["breaking"])})
    return {"comparisons": results, "all_compatible": all(r["compatible"] for r in results)}
