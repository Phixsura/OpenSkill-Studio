"""Snapshot diff — compare configuration snapshots for drift detection."""

import html
from datetime import datetime, timezone


def diff_snapshots(*, before: dict, after: dict) -> dict:
    added = {k: after[k] for k in after if k not in before}
    removed = {k: before[k] for k in before if k not in after}
    changed = {}
    for k in before:
        if k in after and before[k] != after[k]:
            changed[k] = {"before": before[k], "after": after[k]}
    unchanged = {k for k in before if k in after and before[k] == after[k]}
    has_drift = len(added) + len(removed) + len(changed) > 0
    return {"added": added, "removed": removed, "changed": changed,
            "added_count": len(added), "removed_count": len(removed),
            "changed_count": len(changed), "unchanged_count": len(unchanged),
            "has_drift": has_drift, "total_changes": len(added) + len(removed) + len(changed)}
