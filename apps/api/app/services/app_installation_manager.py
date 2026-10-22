"""Installation manager — high-level installation lifecycle operations."""


def validate_upgrade(*, current_version: str, target_version: str, current_permissions: list[str], target_permissions: list[str]) -> dict:
    """Validate an installation upgrade."""
    new_perms = set(target_permissions) - set(current_permissions)
    removed_perms = set(current_permissions) - set(target_permissions)
    return {
        "can_auto_upgrade": len(new_perms) == 0 and len(removed_perms) == 0,
        "needs_consent": len(new_perms) > 0,
        "new_permissions": sorted(new_perms),
        "removed_permissions": sorted(removed_perms),
        "from_version": current_version,
        "to_version": target_version,
    }


def compute_rollback_info(*, current_version: str, previous_version: str | None) -> dict:
    """Compute rollback availability."""
    return {
        "can_rollback": previous_version is not None,
        "current_version": current_version,
        "rollback_target": previous_version,
    }
