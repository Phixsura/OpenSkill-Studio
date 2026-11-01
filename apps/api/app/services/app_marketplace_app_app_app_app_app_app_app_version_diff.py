"""Version diff — compare settings between two app versions."""
from __future__ import annotations


def diff_versions(old: dict, new: dict) -> dict:
    added, removed, changed = [], [], []
    all_keys = set(old) | set(new)
    for k in sorted(all_keys):
        if k not in old:
            added.append({"key": k, "value": new[k]})
        elif k not in new:
            removed.append({"key": k, "value": old[k]})
        elif old[k] != new[k]:
            changed.append({"key": k, "old": old[k], "new": new[k]})
    total = len(added) + len(removed) + len(changed)
    return {"added": added, "removed": removed, "changed": changed,
            "total_changes": total, "has_breaking": len(removed) > 0}
