"""App Changelog Diff — compute diffs between app versions.

Compares two app manifest versions to identify changes:
- Added, removed, and modified fields
- Nested object diffing
- Change summary generation
"""

from __future__ import annotations

from dataclasses import dataclass, field

import structlog

log = structlog.get_logger()


@dataclass
class FieldChange:
    """A change to a single field."""

    path: str
    change_type: str  # "added", "removed", "modified"
    old_value: object = None
    new_value: object = None


@dataclass
class DiffResult:
    """Result of comparing two versions."""

    from_version: str
    to_version: str
    changes: list[FieldChange]
    added_count: int = 0
    removed_count: int = 0
    modified_count: int = 0

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0


class AppChangelogDiff:
    """Compute diffs between app manifest versions."""

    def diff(
        self,
        from_version: str,
        to_version: str,
        old_manifest: dict,
        new_manifest: dict,
    ) -> DiffResult:
        """Compute diff between two manifests."""
        if not from_version:
            raise ValueError("from_version is required")
        if not to_version:
            raise ValueError("to_version is required")

        changes: list[FieldChange] = []
        self._diff_recursive("", old_manifest, new_manifest, changes)

        added = sum(1 for c in changes if c.change_type == "added")
        removed = sum(1 for c in changes if c.change_type == "removed")
        modified = sum(1 for c in changes if c.change_type == "modified")

        return DiffResult(
            from_version=from_version,
            to_version=to_version,
            changes=changes,
            added_count=added,
            removed_count=removed,
            modified_count=modified,
        )

    def summarize(self, result: DiffResult) -> str:
        """Generate a human-readable summary."""
        if not result.has_changes:
            return f"No changes between {result.from_version} and {result.to_version}"

        parts = []
        if result.added_count:
            parts.append(f"{result.added_count} added")
        if result.removed_count:
            parts.append(f"{result.removed_count} removed")
        if result.modified_count:
            parts.append(f"{result.modified_count} modified")

        return f"{result.from_version} → {result.to_version}: {', '.join(parts)}"

    def _diff_recursive(
        self, prefix: str, old: dict, new: dict, changes: list[FieldChange]
    ) -> None:
        all_keys = set(old.keys()) | set(new.keys())

        for key in sorted(all_keys):
            path = f"{prefix}.{key}" if prefix else key
            in_old = key in old
            in_new = key in new

            if in_old and not in_new:
                changes.append(FieldChange(
                    path=path, change_type="removed", old_value=old[key],
                ))
            elif not in_old and in_new:
                changes.append(FieldChange(
                    path=path, change_type="added", new_value=new[key],
                ))
            elif old[key] != new[key]:
                # Recurse into nested dicts
                if isinstance(old[key], dict) and isinstance(new[key], dict):
                    self._diff_recursive(path, old[key], new[key], changes)
                else:
                    changes.append(FieldChange(
                        path=path, change_type="modified",
                        old_value=old[key], new_value=new[key],
                    ))
