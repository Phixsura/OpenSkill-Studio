"""Changelog diff — compare two app versions and highlight changes."""


def diff_versions(*, old_version: dict, new_version: dict) -> dict:
    old_fields = set(old_version.keys())
    new_fields = set(new_version.keys())
    added = new_fields - old_fields
    removed = old_fields - new_fields
    common = old_fields & new_fields
    modified = []
    for key in sorted(common):
        if old_version[key] != new_version[key]:
            modified.append({"field": key, "old": old_version[key], "new": new_version[key]})
    return {
        "added_fields": sorted(added),
        "removed_fields": sorted(removed),
        "modified_fields": modified,
        "unchanged_count": len(common) - len(modified),
        "total_changes": len(added) + len(removed) + len(modified),
        "has_breaking": len(removed) > 0 or any(m["field"] in ("api_version", "entry_point", "permissions") for m in modified),
    }


def summarize_diff(*, diff: dict) -> str:
    parts = []
    if diff["added_fields"]:
        parts.append(f"Added: {', '.join(diff['added_fields'])}")
    if diff["removed_fields"]:
        parts.append(f"Removed: {', '.join(diff['removed_fields'])}")
    if diff["modified_fields"]:
        parts.append(f"Modified: {', '.join(m['field'] for m in diff['modified_fields'])}")
    return "; ".join(parts) if parts else "No changes"
