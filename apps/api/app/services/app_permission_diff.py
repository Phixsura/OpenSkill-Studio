"""Permission diff — compute and explain permission changes between versions."""


def diff_permissions(old: list[str], new: list[str]) -> dict:
    """Compute permission diff with categorized changes."""
    old_set, new_set = set(old), set(new)
    added = sorted(new_set - old_set)
    removed = sorted(old_set - new_set)
    unchanged = sorted(old_set & new_set)

    # Categorize by action type
    read_added = [p for p in added if p.startswith("read:")]
    write_added = [p for p in added if p.startswith("write:")]
    special_added = [p for p in added if not p.startswith(("read:", "write:"))]

    return {
        "added": added,
        "removed": removed,
        "unchanged": unchanged,
        "total_before": len(old),
        "total_after": len(new),
        "breaking": len(removed) > 0,
        "needs_consent": len(added) > 0,
        "read_added": read_added,
        "write_added": write_added,
        "special_added": special_added,
    }


def format_permission_diff(diff: dict) -> str:
    """Format permission diff as human-readable text."""
    lines = []
    if diff["added"]:
        lines.append(f"+ Added: {', '.join(diff['added'])}")
    if diff["removed"]:
        lines.append(f"- Removed: {', '.join(diff['removed'])}")
    if not lines:
        lines.append("No permission changes")
    return "\n".join(lines)
