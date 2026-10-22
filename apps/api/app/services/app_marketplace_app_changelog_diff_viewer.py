"""Changelog diff viewer — compare changes between any two versions."""


def compute_version_diff(*, old_version: dict, new_version: dict) -> dict:
    old_perms = set(old_version.get("permissions", []))
    new_perms = set(new_version.get("permissions", []))
    old_endpoints = set(old_version.get("endpoints", []))
    new_endpoints = set(new_version.get("endpoints", []))
    old_config_keys = set(old_version.get("config_schema", {}).keys())
    new_config_keys = set(new_version.get("config_schema", {}).keys())
    return {
        "permissions": {"added": sorted(new_perms - old_perms), "removed": sorted(old_perms - new_perms)},
        "endpoints": {"added": sorted(new_endpoints - old_endpoints), "removed": sorted(old_endpoints - new_endpoints)},
        "config": {"added": sorted(new_config_keys - old_config_keys), "removed": sorted(old_config_keys - new_config_keys)},
        "has_breaking": bool((old_perms - new_perms) or (old_endpoints - new_endpoints) or (old_config_keys - new_config_keys)),
        "total_changes": len(new_perms ^ old_perms) + len(new_endpoints ^ old_endpoints) + len(new_config_keys ^ old_config_keys),
    }
