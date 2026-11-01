"""Version comparison — compare two versions of an app side by side."""

def compare_versions(v1: dict, v2: dict) -> dict:
    perms1, perms2 = set(v1.get("permissions", [])), set(v2.get("permissions", []))
    return {
        "v1": v1.get("version"), "v2": v2.get("version"),
        "permissions_added": sorted(perms2 - perms1), "permissions_removed": sorted(perms1 - perms2),
        "sandbox_changed": v1.get("sandbox") != v2.get("sandbox"),
        "breaking": bool(perms1 - perms2),
    }
