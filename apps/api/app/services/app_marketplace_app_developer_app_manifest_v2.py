"""App manifest v2 — enhanced manifest with validation, diffing, and migration."""

import json


def validate_manifest_v2(*, manifest: dict) -> dict:
    errors = []
    required = ["name", "version", "entry_point", "permissions"]
    for field in required:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")
    if "version" in manifest and not isinstance(manifest["version"], str):
        errors.append("Version must be a string")
    perms = manifest.get("permissions", [])
    if not isinstance(perms, list):
        errors.append("Permissions must be an array")
    entry = manifest.get("entry_point", "")
    if entry and not entry.endswith((".js", ".ts", ".py")):
        errors.append("Entry point must be .js, .ts, or .py file")
    return {"valid": len(errors) == 0, "errors": errors, "field_count": len(manifest)}


def diff_manifests(*, old: dict, new: dict) -> dict:
    changes = []
    all_keys = set(old.keys()) | set(new.keys())
    for key in sorted(all_keys):
        old_val = old.get(key)
        new_val = new.get(key)
        if old_val != new_val:
            changes.append({"field": key, "old": old_val, "new": new_val,
                            "type": "added" if old_val is None else "removed" if new_val is None else "changed"})
    return {"changes": changes, "change_count": len(changes), "has_breaking": any(c["type"] == "removed" for c in changes)}
