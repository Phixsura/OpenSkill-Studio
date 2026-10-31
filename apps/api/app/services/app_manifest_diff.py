"""App Manifest Diff — structured comparison of app manifests across versions.

Computes a human-readable diff between two app manifest versions:
- Field-level change detection (added, removed, modified, unchanged)
- Permission diff (added/removed scopes)
- Config schema diff (new/removed fields, type changes)
- Extension surface diff
- Severity classification per change
- Summary statistics
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum

import structlog

log = structlog.get_logger()


class ChangeKind(str, Enum):
    ADDED = "added"
    REMOVED = "removed"
    MODIFIED = "modified"
    UNCHANGED = "unchanged"


class ChangeSeverity(str, Enum):
    NONE = "none"
    PATCH = "patch"
    MINOR = "minor"
    BREAKING = "breaking"


@dataclass
class FieldChange:
    """A change to a single manifest field."""

    field_path: str
    kind: ChangeKind
    severity: ChangeSeverity
    old_value: object = None
    new_value: object = None


@dataclass
class ManifestDiffResult:
    """Complete diff between two manifest versions."""

    from_version: str
    to_version: str
    changes: list[FieldChange]
    added_permissions: list[str]
    removed_permissions: list[str]
    added_config_fields: list[str]
    removed_config_fields: list[str]
    added_surfaces: list[str]
    removed_surfaces: list[str]
    has_breaking: bool
    summary: str

    @property
    def total_changes(self) -> int:
        return len([c for c in self.changes if c.kind != ChangeKind.UNCHANGED])


# Fields that trigger breaking changes when modified or removed
BREAKING_FIELDS = {"min_platform_version", "required_permissions", "oauth_redirect_uris"}

# Fields that are cosmetic (patch-level)
PATCH_FIELDS = {"description", "icon_url", "homepage_url", "changelog", "tags"}


def diff_manifests(old: dict, new: dict,
                   from_version: str = "old",
                   to_version: str = "new") -> ManifestDiffResult:
    """Compute a structured diff between two manifest dicts."""
    changes: list[FieldChange] = []

    all_keys = sorted(set(list(old.keys()) + list(new.keys())))

    for key in all_keys:
        if key not in old:
            sev = ChangeSeverity.MINOR
            changes.append(FieldChange(key, ChangeKind.ADDED, sev, new_value=new[key]))
        elif key not in new:
            sev = ChangeSeverity.BREAKING if key in BREAKING_FIELDS else ChangeSeverity.MINOR
            changes.append(FieldChange(key, ChangeKind.REMOVED, sev, old_value=old[key]))
        elif old[key] != new[key]:
            sev = _classify_change(key, old[key], new[key])
            changes.append(FieldChange(key, ChangeKind.MODIFIED, sev,
                                        old_value=old[key], new_value=new[key]))
        else:
            changes.append(FieldChange(key, ChangeKind.UNCHANGED, ChangeSeverity.NONE,
                                        old_value=old[key], new_value=new[key]))

    # Permission diff
    old_perms = set(old.get("permissions", []))
    new_perms = set(new.get("permissions", []))
    added_perms = sorted(new_perms - old_perms)
    removed_perms = sorted(old_perms - new_perms)

    # Config diff
    old_config = set(old.get("config_fields", {}).keys() if isinstance(old.get("config_fields"), dict) else [])
    new_config = set(new.get("config_fields", {}).keys() if isinstance(new.get("config_fields"), dict) else [])
    added_cfg = sorted(new_config - old_config)
    removed_cfg = sorted(old_config - new_config)

    # Surface diff
    old_surfaces = set(old.get("extension_surfaces", []))
    new_surfaces = set(new.get("extension_surfaces", []))
    added_surf = sorted(new_surfaces - old_surfaces)
    removed_surf = sorted(old_surfaces - new_surfaces)

    has_breaking = any(c.severity == ChangeSeverity.BREAKING for c in changes) or bool(removed_perms)

    # Summary
    total = len([c for c in changes if c.kind != ChangeKind.UNCHANGED])
    breaking_count = len([c for c in changes if c.severity == ChangeSeverity.BREAKING])
    summary = f"{total} changes ({breaking_count} breaking)"
    if added_perms:
        summary += f", +{len(added_perms)} permissions"
    if removed_perms:
        summary += f", -{len(removed_perms)} permissions"

    return ManifestDiffResult(
        from_version=from_version,
        to_version=to_version,
        changes=changes,
        added_permissions=added_perms,
        removed_permissions=removed_perms,
        added_config_fields=added_cfg,
        removed_config_fields=removed_cfg,
        added_surfaces=added_surf,
        removed_surfaces=removed_surf,
        has_breaking=has_breaking,
        summary=summary,
    )


def _classify_change(key: str, old_val: object, new_val: object) -> ChangeSeverity:
    """Classify the severity of a field modification."""
    if key in BREAKING_FIELDS:
        return ChangeSeverity.BREAKING
    if key in PATCH_FIELDS:
        return ChangeSeverity.PATCH
    if key == "permissions":
        old_set = set(old_val) if isinstance(old_val, list) else set()
        new_set = set(new_val) if isinstance(new_val, list) else set()
        if old_set - new_set:  # removed permissions = breaking
            return ChangeSeverity.BREAKING
        return ChangeSeverity.MINOR
    if key == "config_fields":
        if isinstance(old_val, dict) and isinstance(new_val, dict):
            if set(old_val.keys()) - set(new_val.keys()):  # removed fields
                return ChangeSeverity.BREAKING
        return ChangeSeverity.MINOR
    return ChangeSeverity.MINOR
