"""Permission validation service for app installations.

Validates that requested operations are covered by the installation's
granted permissions, and checks permission compatibility on upgrades.
"""

import structlog

log = structlog.get_logger()

# Map API path patterns to required permissions
PATH_PERMISSION_MAP = {
    "cohorts": "read:cohorts",
    "projects": "read:projects",
    "submissions": "read:submissions",
    "skills": "read:skills",
    "packs": "read:packs",
    "workflows": "read:workflows",
    "providers": "read:providers",
    "talent": "read:talent",
    "evaluations": "read:evaluations",
    "matching": "read:matching",
    "marketplace": "read:marketplace",
    "users": "read:users",
    "analytics": "read:analytics",
    "settings": "read:settings",
}

# Write operations require write scopes
WRITE_PERMISSION_MAP = {
    "cohorts": "write:cohorts",
    "projects": "write:projects",
    "skills": "write:skills",
    "packs": "write:packs",
    "workflows": "write:workflows",
    "providers": "write:providers",
    "talent": "write:talent",
    "evaluations": "write:evaluations",
    "matching": "write:matching",
    "marketplace": "write:marketplace_listings",
    "settings": "write:settings",
}


def check_permission(
    granted_permissions: list[str],
    resource: str,
    is_write: bool = False,
) -> bool:
    """Check if an operation is allowed by granted permissions.

    Args:
        granted_permissions: List of scopes granted to the installation
        resource: The resource being accessed (e.g., "cohorts", "projects")
        is_write: Whether the operation modifies data

    Returns:
        True if the operation is allowed
    """
    perm_map = WRITE_PERMISSION_MAP if is_write else PATH_PERMISSION_MAP
    required = perm_map.get(resource)

    if not required:
        return True  # Unknown resource — not restricted

    return required in granted_permissions


def get_missing_permissions(
    granted: list[str],
    required: list[str],
) -> list[str]:
    """Get permissions that are required but not granted."""
    granted_set = set(granted)
    return [p for p in required if p not in granted_set]


def validate_installation_permissions(
    manifest_permissions: list[str],
    granted_permissions: list[str],
) -> dict:
    """Validate that granted permissions are a subset of manifest permissions.

    Returns a report with any issues found.
    """
    manifest_set = set(manifest_permissions)
    granted_set = set(granted_permissions)

    # Granted permissions that aren't in the manifest
    extra = granted_set - manifest_set
    # Manifest permissions not granted
    ungrated = manifest_set - granted_set

    return {
        "valid": len(extra) == 0,
        "extra_permissions": sorted(extra),
        "ungranted_permissions": sorted(ungrated),
        "granted_count": len(granted_set),
        "manifest_count": len(manifest_set),
    }


def get_permission_summary(permissions: list[str]) -> dict:
    """Summarize permissions by category."""
    categories: dict[str, list[str]] = {}
    for perm in sorted(permissions):
        parts = perm.split(":")
        category = parts[0] if parts else "other"
        categories.setdefault(category, []).append(perm)

    return {
        "total": len(permissions),
        "categories": categories,
        "read_count": sum(1 for p in permissions if p.startswith("read:")),
        "write_count": sum(1 for p in permissions if p.startswith("write:")),
        "special_count": sum(
            1 for p in permissions if not p.startswith(("read:", "write:"))
        ),
    }
