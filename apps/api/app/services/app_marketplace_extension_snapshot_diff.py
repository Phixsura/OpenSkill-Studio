"""Snapshot Diff — compute diffs between extension versions.

Compares two versions of an extension and produces a structured
diff showing added, removed, and modified files and config changes.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class FileDiff:
    path: str
    status: str  # "added", "removed", "modified", "unchanged"
    old_size: int = 0
    new_size: int = 0
    size_delta: int = 0


@dataclass
class VersionDiff:
    extension_id: str
    from_version: str
    to_version: str
    files: list[FileDiff] = field(default_factory=list)
    config_changes: dict = field(default_factory=dict)
    permissions_added: list[str] = field(default_factory=list)
    permissions_removed: list[str] = field(default_factory=list)


class SnapshotDiffService:
    """Computes structured diffs between extension versions."""

    def diff_files(self, old_files: dict[str, int], new_files: dict[str, int]) -> list[FileDiff]:
        """Diff two file listings. {path: size_bytes}."""
        diffs = []
        all_paths = sorted(set(old_files.keys()) | set(new_files.keys()))

        for path in all_paths:
            old_size = old_files.get(path, 0)
            new_size = new_files.get(path, 0)

            if path not in old_files:
                diffs.append(FileDiff(path, "added", 0, new_size, new_size))
            elif path not in new_files:
                diffs.append(FileDiff(path, "removed", old_size, 0, -old_size))
            elif old_size != new_size:
                diffs.append(FileDiff(path, "modified", old_size, new_size, new_size - old_size))
            else:
                diffs.append(FileDiff(path, "unchanged", old_size, new_size, 0))

        return diffs

    def diff_permissions(self, old_perms: list[str], new_perms: list[str]) -> tuple[list[str], list[str]]:
        """Return (added, removed) permissions."""
        old_set = set(old_perms)
        new_set = set(new_perms)
        return sorted(new_set - old_set), sorted(old_set - new_set)

    def diff_config(self, old_config: dict, new_config: dict) -> dict:
        """Diff two config dicts. Returns {added, removed, changed, unchanged}."""
        old_keys = set(old_config.keys())
        new_keys = set(new_config.keys())
        return {
            "added": {k: new_config[k] for k in sorted(new_keys - old_keys)},
            "removed": sorted(old_keys - new_keys),
            "changed": {k: {"old": old_config[k], "new": new_config[k]}
                        for k in sorted(old_keys & new_keys) if old_config[k] != new_config[k]},
            "unchanged": sorted(k for k in old_keys & new_keys if old_config[k] == new_config[k]),
        }

    def compute_full_diff(self, extension_id: str, from_ver: str, to_ver: str,
                          old_files: dict[str, int], new_files: dict[str, int],
                          old_perms: list[str], new_perms: list[str],
                          old_config: dict, new_config: dict) -> VersionDiff:
        """Compute a complete version diff."""
        added, removed = self.diff_permissions(old_perms, new_perms)
        return VersionDiff(
            extension_id=extension_id, from_version=from_ver, to_version=to_ver,
            files=self.diff_files(old_files, new_files),
            config_changes=self.diff_config(old_config, new_config),
            permissions_added=added, permissions_removed=removed,
        )

    def get_summary(self, diff: VersionDiff) -> dict:
        """Get a summary of the diff."""
        by_status = {"added": 0, "removed": 0, "modified": 0, "unchanged": 0}
        total_delta = 0
        for f in diff.files:
            by_status[f.status] += 1
            total_delta += f.size_delta
        return {
            "extension_id": diff.extension_id,
            "from": diff.from_version, "to": diff.to_version,
            "files": by_status,
            "size_delta_bytes": total_delta,
            "permissions_added": len(diff.permissions_added),
            "permissions_removed": len(diff.permissions_removed),
            "config_changes": len(diff.config_changes.get("changed", {})),
            "breaking": len(diff.permissions_removed) > 0 or len(diff.config_changes.get("removed", [])) > 0,
        }
