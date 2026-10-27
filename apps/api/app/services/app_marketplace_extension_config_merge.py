"""Config Merge — deep merge multiple config sources with conflict resolution.

Merge configs from: defaults < file < env < CLI < override.

Implements:
- Deep merge nested dicts (not just shallow)
- Conflict resolution: last-wins, first-wins, error-on-conflict
- Type-safe merge (reject type changes unless explicitly allowed)
- Merge path tracking (know which source each value came from)
- Array merge strategies: replace, append, unique
"""
from __future__ import annotations
from dataclasses import dataclass, field
from copy import deepcopy


@dataclass
class MergeResult:
    merged: dict
    conflicts: list[dict] = field(default_factory=list)
    sources: dict = field(default_factory=dict)  # path → source name


class ConfigMergeService:
    def merge(self, *configs: tuple[str, dict],
              strategy: str = "last_wins",
              array_strategy: str = "replace",
              type_safe: bool = False) -> MergeResult:
        """Merge multiple named configs. configs = [(name, dict), ...]
        strategy: last_wins, first_wins, error
        array_strategy: replace, append, unique"""
        result = MergeResult(merged={})

        for name, config in configs:
            self._deep_merge(result.merged, config, name, result,
                             strategy, array_strategy, type_safe, "")

        return result

    def _deep_merge(self, target: dict, source: dict, source_name: str,
                    result: MergeResult, strategy: str,
                    array_strategy: str, type_safe: bool,
                    path_prefix: str) -> None:
        for key, new_value in source.items():
            path = f"{path_prefix}.{key}" if path_prefix else key

            if key not in target:
                target[key] = deepcopy(new_value)
                result.sources[path] = source_name
                continue

            old_value = target[key]

            # Both dicts → recursive merge
            if isinstance(old_value, dict) and isinstance(new_value, dict):
                self._deep_merge(old_value, new_value, source_name, result,
                                 strategy, array_strategy, type_safe, path)
                continue

            # Type mismatch check
            if type_safe and type(old_value) != type(new_value):
                result.conflicts.append({
                    "path": path, "type": "type_mismatch",
                    "old_type": type(old_value).__name__,
                    "new_type": type(new_value).__name__,
                    "source": source_name})
                if strategy == "error":
                    continue  # keep old on error
                # Otherwise fall through to normal merge

            # Array merge
            if isinstance(old_value, list) and isinstance(new_value, list):
                if array_strategy == "append":
                    target[key] = old_value + new_value
                elif array_strategy == "unique":
                    seen = set()
                    merged_list = []
                    for item in old_value + new_value:
                        item_key = str(item)
                        if item_key not in seen:
                            seen.add(item_key)
                            merged_list.append(item)
                    target[key] = merged_list
                else:  # replace
                    target[key] = deepcopy(new_value)
                result.sources[path] = source_name
                continue

            # Scalar conflict
            if old_value != new_value:
                result.conflicts.append({
                    "path": path, "type": "value_conflict",
                    "old": old_value, "new": new_value,
                    "source": source_name})

            if strategy == "last_wins":
                target[key] = deepcopy(new_value)
                result.sources[path] = source_name
            elif strategy == "first_wins":
                pass  # keep old
            elif strategy == "error":
                pass  # keep old, conflict recorded

    def overlay(self, base: dict, *overlays: dict) -> dict:
        """Simple last-wins merge (convenience method)."""
        configs = [("base", base)] + [(f"overlay-{i}", o) for i, o in enumerate(overlays)]
        return self.merge(*configs).merged

    def diff(self, a: dict, b: dict, path: str = "") -> list[dict]:
        """Find differences between two configs."""
        diffs = []
        all_keys = set(a) | set(b)
        for key in sorted(all_keys):
            full_path = f"{path}.{key}" if path else key
            if key not in a:
                diffs.append({"path": full_path, "type": "added", "value": b[key]})
            elif key not in b:
                diffs.append({"path": full_path, "type": "removed", "value": a[key]})
            elif isinstance(a[key], dict) and isinstance(b[key], dict):
                diffs.extend(self.diff(a[key], b[key], full_path))
            elif a[key] != b[key]:
                diffs.append({"path": full_path, "type": "changed",
                              "old": a[key], "new": b[key]})
        return diffs
