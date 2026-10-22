"""App compatibility checking (ADR-016 Part P).

Validates that app versions are compatible with the current platform version,
and that upgrades won't break existing installations.
"""

import re

import structlog

log = structlog.get_logger()

# Current platform version
PLATFORM_VERSION = "1.0.0"


def parse_semver(version: str) -> tuple[int, int, int] | None:
    """Parse a semver string into (major, minor, patch)."""
    m = re.match(r"^(\d+)\.(\d+)\.(\d+)", version)
    if not m:
        return None
    return int(m.group(1)), int(m.group(2)), int(m.group(3))


def is_compatible(min_platform_version: str | None) -> bool:
    """Check if an app version is compatible with the current platform."""
    if not min_platform_version:
        return True  # No minimum specified = compatible

    required = parse_semver(min_platform_version)
    current = parse_semver(PLATFORM_VERSION)

    if not required or not current:
        return True  # Can't parse = assume compatible

    return current >= required


def check_upgrade_compatibility(
    current_manifest: dict | None,
    new_manifest: dict | None,
) -> dict:
    """Check if upgrading from current to new manifest is safe.

    Returns a report with breaking changes, warnings, and compatibility status.
    """
    report = {
        "compatible": True,
        "breaking_changes": [],
        "warnings": [],
        "permissions_added": [],
        "permissions_removed": [],
    }

    if not current_manifest or not new_manifest:
        return report

    # Check permission changes
    old_perms = set(current_manifest.get("permissions", []))
    new_perms = set(new_manifest.get("permissions", []))

    added = new_perms - old_perms
    removed = old_perms - new_perms

    if added:
        report["permissions_added"] = sorted(added)
        report["warnings"].append(
            f"New permissions requested: {', '.join(sorted(added))}"
        )

    if removed:
        report["permissions_removed"] = sorted(removed)
        # Removing permissions is not breaking but worth noting
        report["warnings"].append(
            f"Permissions removed: {', '.join(sorted(removed))}"
        )

    # Check schema version compatibility
    old_schema = current_manifest.get("schema_version", "1.0")
    new_schema = new_manifest.get("schema_version", "1.0")
    if old_schema != new_schema:
        old_major = old_schema.split(".")[0]
        new_major = new_schema.split(".")[0]
        if old_major != new_major:
            report["breaking_changes"].append(
                f"Schema version major change: {old_schema} → {new_schema}"
            )
            report["compatible"] = False

    # Check UI extension surface changes
    old_surfaces = {
        ext.get("surface")
        for ext in current_manifest.get("ui_extensions", [])
        if isinstance(ext, dict)
    }
    new_surfaces = {
        ext.get("surface")
        for ext in new_manifest.get("ui_extensions", [])
        if isinstance(ext, dict)
    }
    removed_surfaces = old_surfaces - new_surfaces
    if removed_surfaces:
        report["breaking_changes"].append(
            f"UI surfaces removed: {', '.join(s for s in sorted(removed_surfaces) if s)}"
        )

    # Check event subscription changes
    old_events = set(current_manifest.get("event_subscriptions", []))
    new_events = set(new_manifest.get("event_subscriptions", []))
    removed_events = old_events - new_events
    if removed_events:
        report["warnings"].append(
            f"Event subscriptions removed: {', '.join(sorted(removed_events))}"
        )

    # Check secret requirements
    old_secrets = {
        s.get("key") for s in current_manifest.get("secrets", [])
        if isinstance(s, dict) and s.get("required")
    }
    new_secrets = {
        s.get("key") for s in new_manifest.get("secrets", [])
        if isinstance(s, dict) and s.get("required")
    }
    new_required = new_secrets - old_secrets
    if new_required:
        report["warnings"].append(
            f"New required secrets: {', '.join(s for s in sorted(new_required) if s)}"
        )

    # Check platform version compatibility
    new_min = new_manifest.get("app", {}).get("min_platform_version")
    if new_min and not is_compatible(new_min):
        report["breaking_changes"].append(
            f"Requires platform {new_min}, current is {PLATFORM_VERSION}"
        )
        report["compatible"] = False

    if report["breaking_changes"]:
        report["compatible"] = False

    return report
