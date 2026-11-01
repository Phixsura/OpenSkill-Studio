"""Installation config merger — merge app defaults with org overrides."""

import copy


def merge_installation_config(*, app_defaults: dict, org_overrides: dict | None = None) -> dict:
    """Merge org-specific overrides on top of app default config."""
    result = copy.deepcopy(app_defaults)
    if org_overrides:
        result.update(org_overrides)
    return result


def diff_config(current: dict, proposed: dict) -> dict:
    """Diff two config dicts."""
    added = {k: v for k, v in proposed.items() if k not in current}
    removed = {k: v for k, v in current.items() if k not in proposed}
    changed = {k: {"from": current[k], "to": proposed[k]} for k in current if k in proposed and current[k] != proposed[k]}
    return {"added": added, "removed": removed, "changed": changed, "has_changes": bool(added or removed or changed)}
