"""API schema versioning — track and compare API schema versions."""
from __future__ import annotations


def compare_schemas(old: dict, new: dict) -> dict:
    old_fields = set(old.get("fields", {}).keys())
    new_fields = set(new.get("fields", {}).keys())
    added = sorted(new_fields - old_fields)
    removed = sorted(old_fields - new_fields)
    changed = []
    for f in sorted(old_fields & new_fields):
        if old["fields"][f] != new["fields"][f]:
            changed.append({"field": f, "old": old["fields"][f], "new": new["fields"][f]})
    breaking = len(removed) > 0 or len(changed) > 0
    bump = "major" if breaking else ("minor" if added else "patch")
    return {"added": added, "removed": removed, "changed": changed,
            "breaking": breaking, "suggested_bump": bump,
            "total_changes": len(added) + len(removed) + len(changed)}


def version_history(versions: list[dict]) -> dict:
    sorted_v = sorted(versions, key=lambda v: v.get("released_at", ""), reverse=True)
    return {"versions": sorted_v, "total": len(sorted_v),
            "latest": sorted_v[0]["version"] if sorted_v else None}
