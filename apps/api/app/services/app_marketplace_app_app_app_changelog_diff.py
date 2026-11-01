"""App changelog diff — diff between two app versions."""

import html


def diff_versions(*, old_version: dict, new_version: dict) -> dict:
    old_features = set(old_version.get("features", []))
    new_features = set(new_version.get("features", []))
    added = new_features - old_features
    removed = old_features - new_features
    old_perms = set(old_version.get("permissions", []))
    new_perms = set(new_version.get("permissions", []))
    new_permissions = new_perms - old_perms
    removed_permissions = old_perms - new_perms
    config_changes = []
    for key in set(list(old_version.get("config", {}).keys()) + list(new_version.get("config", {}).keys())):
        old_val = old_version.get("config", {}).get(key)
        new_val = new_version.get("config", {}).get(key)
        if old_val != new_val:
            config_changes.append({"key": key, "old": old_val, "new": new_val})
    return {
        "old_version": old_version.get("version", ""),
        "new_version": new_version.get("version", ""),
        "features_added": sorted(added),
        "features_removed": sorted(removed),
        "permissions_added": sorted(new_permissions),
        "permissions_removed": sorted(removed_permissions),
        "config_changes": config_changes,
        "total_changes": len(added) + len(removed) + len(new_permissions) + len(removed_permissions) + len(config_changes),
        "has_breaking": len(removed) > 0 or len(removed_permissions) > 0,
    }
