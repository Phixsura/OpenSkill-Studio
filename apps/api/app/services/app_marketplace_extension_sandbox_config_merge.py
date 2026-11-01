"""Sandbox Config Merge — deep merge extension configs with conflict resolution.

Merges multiple config sources (defaults, user, environment, overrides)
with deep merge, array handling strategies, and merge conflict detection.
"""
from __future__ import annotations
import copy
from dataclasses import dataclass, field
from enum import Enum


class ArrayStrategy(str, Enum):
    REPLACE = "replace"
    APPEND = "append"
    UNIQUE = "unique"


class ConflictStrategy(str, Enum):
    LAST_WINS = "last_wins"
    FIRST_WINS = "first_wins"
    ERROR = "error"


@dataclass
class MergeConflict:
    path: str
    values: list
    resolved_value: object = None


@dataclass
class MergeResult:
    merged: dict
    conflicts: list[MergeConflict] = field(default_factory=list)
    sources_merged: int = 0


class SandboxConfigMergeService:
    """Deep merges config sources with conflict resolution."""

    def merge(self, sources: list[dict],
              array_strategy: ArrayStrategy = ArrayStrategy.REPLACE,
              conflict_strategy: ConflictStrategy = ConflictStrategy.LAST_WINS) -> MergeResult:
        if not sources:
            return MergeResult(merged={}, sources_merged=0)

        result = copy.deepcopy(sources[0])
        conflicts: list[MergeConflict] = []

        for i in range(1, len(sources)):
            self._deep_merge(result, sources[i], "", conflicts,
                             array_strategy, conflict_strategy)

        return MergeResult(
            merged=result, conflicts=conflicts,
            sources_merged=len(sources),
        )

    def _deep_merge(self, base: dict, override: dict, prefix: str,
                    conflicts: list[MergeConflict],
                    array_strategy: ArrayStrategy,
                    conflict_strategy: ConflictStrategy) -> None:
        for key, new_val in override.items():
            path = f"{prefix}.{key}" if prefix else key

            if key not in base:
                base[key] = copy.deepcopy(new_val)
                continue

            old_val = base[key]

            # Both are dicts — recurse
            if isinstance(old_val, dict) and isinstance(new_val, dict):
                self._deep_merge(old_val, new_val, path, conflicts,
                                 array_strategy, conflict_strategy)
                continue

            # Both are arrays — apply strategy
            if isinstance(old_val, list) and isinstance(new_val, list):
                if array_strategy == ArrayStrategy.REPLACE:
                    base[key] = copy.deepcopy(new_val)
                elif array_strategy == ArrayStrategy.APPEND:
                    base[key] = old_val + copy.deepcopy(new_val)
                elif array_strategy == ArrayStrategy.UNIQUE:
                    combined = old_val + [v for v in new_val if v not in old_val]
                    base[key] = combined
                continue

            # Conflict: same key, different values
            if old_val != new_val:
                conflict = MergeConflict(path=path, values=[old_val, new_val])
                if conflict_strategy == ConflictStrategy.LAST_WINS:
                    base[key] = copy.deepcopy(new_val)
                    conflict.resolved_value = new_val
                elif conflict_strategy == ConflictStrategy.FIRST_WINS:
                    conflict.resolved_value = old_val
                elif conflict_strategy == ConflictStrategy.ERROR:
                    conflict.resolved_value = None
                conflicts.append(conflict)
            # else: same value, no conflict

    def diff(self, config_a: dict, config_b: dict) -> dict:
        added = {k: config_b[k] for k in config_b if k not in config_a}
        removed = {k: config_a[k] for k in config_a if k not in config_b}
        changed = {k: {"from": config_a[k], "to": config_b[k]}
                   for k in config_a if k in config_b and config_a[k] != config_b[k]}
        return {"added": added, "removed": removed, "changed": changed,
                "has_diff": bool(added or removed or changed)}
