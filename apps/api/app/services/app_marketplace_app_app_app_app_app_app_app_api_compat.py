"""API compatibility checker — verify backward compatibility."""
from __future__ import annotations


def check_compatibility(old_spec: dict, new_spec: dict) -> dict:
    breaking = []
    compatible = []
    old_paths = set(old_spec.get("paths", {}).keys())
    new_paths = set(new_spec.get("paths", {}).keys())
    removed = old_paths - new_paths
    added = new_paths - old_paths
    for p in removed:
        breaking.append({"type": "endpoint_removed", "path": p})
    for p in added:
        compatible.append({"type": "endpoint_added", "path": p})
    for p in old_paths & new_paths:
        old_methods = set(old_spec["paths"][p].keys())
        new_methods = set(new_spec["paths"][p].keys())
        for m in old_methods - new_methods:
            breaking.append({"type": "method_removed", "path": p, "method": m})
    return {"compatible": len(breaking) == 0, "breaking_changes": breaking,
            "compatible_changes": compatible, "breaking_count": len(breaking),
            "compatible_count": len(compatible)}
