"""Manifest field-level differ — detailed field comparison."""


def diff_fields(old: dict, new: dict, prefix: str = "") -> list[dict]:
    """Compare two dicts field by field, returning list of changes."""
    changes = []
    all_keys = set(list(old.keys()) + list(new.keys()))

    for key in sorted(all_keys):
        path = f"{prefix}.{key}" if prefix else key
        old_val = old.get(key)
        new_val = new.get(key)

        if old_val is None and new_val is not None:
            changes.append({"path": path, "type": "added", "value": new_val})
        elif old_val is not None and new_val is None:
            changes.append({"path": path, "type": "removed", "old_value": old_val})
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            changes.extend(diff_fields(old_val, new_val, prefix=path))
        elif old_val != new_val:
            changes.append({"path": path, "type": "changed", "old_value": old_val, "new_value": new_val})

    return changes


def summarize_changes(changes: list[dict]) -> dict:
    """Summarize field changes by type."""
    return {
        "total": len(changes),
        "added": sum(1 for c in changes if c["type"] == "added"),
        "removed": sum(1 for c in changes if c["type"] == "removed"),
        "changed": sum(1 for c in changes if c["type"] == "changed"),
    }
