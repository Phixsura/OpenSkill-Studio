"""Changelog comparison v2 — diff any two versions with highlighted changes."""


def compare_versions_v2(*, version_a: dict, version_b: dict) -> dict:
    a_changes = {c.get("description", ""): c for c in version_a.get("changes", [])}
    b_changes = {c.get("description", ""): c for c in version_b.get("changes", [])}
    only_a = [a_changes[k] for k in set(a_changes) - set(b_changes)]
    only_b = [b_changes[k] for k in set(b_changes) - set(a_changes)]
    common = [a_changes[k] for k in set(a_changes) & set(b_changes)]
    # Permission changes
    a_perms = set(version_a.get("permissions", []))
    b_perms = set(version_b.get("permissions", []))
    perm_added = sorted(b_perms - a_perms)
    perm_removed = sorted(a_perms - b_perms)
    return {
        "version_a": version_a.get("version"), "version_b": version_b.get("version"),
        "only_in_a": only_a, "only_in_b": only_b, "common": common,
        "permissions_added": perm_added, "permissions_removed": perm_removed,
        "has_breaking": len(perm_removed) > 0 or any(c.get("breaking") for c in only_b),
        "total_differences": len(only_a) + len(only_b) + len(perm_added) + len(perm_removed),
    }


def build_migration_notes(*, comparison: dict) -> list[str]:
    notes = []
    if comparison.get("permissions_removed"):
        notes.append(f"⚠️ Permissions removed: {', '.join(comparison['permissions_removed'])}")
    if comparison.get("permissions_added"):
        notes.append(f"🆕 New permissions required: {', '.join(comparison['permissions_added'])}")
    if comparison.get("has_breaking"):
        notes.append("⚠️ This update contains breaking changes — review before updating")
    if not notes:
        notes.append("✅ Safe to update — no breaking changes detected")
    return notes
