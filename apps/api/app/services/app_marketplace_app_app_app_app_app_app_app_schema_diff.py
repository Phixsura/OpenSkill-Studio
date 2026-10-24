"""API schema diff — compare API schemas between versions."""
from __future__ import annotations


def diff_schemas(old_fields: list[str], new_fields: list[str]) -> dict:
    old_set = set(old_fields)
    new_set = set(new_fields)
    added = sorted(new_set - old_set)
    removed = sorted(old_set - new_set)
    unchanged = sorted(old_set & new_set)
    breaking = len(removed) > 0
    return {"added": added, "removed": removed, "unchanged": unchanged,
            "added_count": len(added), "removed_count": len(removed),
            "breaking": breaking, "total_changes": len(added) + len(removed)}


def schema_compatibility(diffs: list[dict]) -> dict:
    total_breaking = sum(1 for d in diffs if d.get("breaking"))
    total_changes = sum(d.get("total_changes", 0) for d in diffs)
    return {"schemas_checked": len(diffs), "total_breaking": total_breaking,
            "total_changes": total_changes,
            "compatible": total_breaking == 0}
