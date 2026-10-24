"""Change diff analyzer — analyze configuration and code diffs."""
from __future__ import annotations


def analyze_diff(old: dict, new: dict) -> dict:
    added = {k: v for k, v in new.items() if k not in old}
    removed = {k: v for k, v in old.items() if k not in new}
    changed = {}
    for k in set(old) & set(new):
        if old[k] != new[k]:
            changed[k] = {"old": old[k], "new": new[k]}
    total = len(added) + len(removed) + len(changed)
    risk = "high" if removed or changed else ("low" if added else "none")
    return {"added": added, "removed": removed, "changed": changed,
            "total_changes": total, "risk": risk}


def summarize_diffs(diffs: list[dict]) -> dict:
    total_added = sum(len(d.get("added", {})) for d in diffs)
    total_removed = sum(len(d.get("removed", {})) for d in diffs)
    total_changed = sum(len(d.get("changed", {})) for d in diffs)
    high_risk = sum(1 for d in diffs if d.get("risk") == "high")
    return {"total_diffs": len(diffs), "total_added": total_added,
            "total_removed": total_removed, "total_changed": total_changed,
            "high_risk": high_risk}
