"""Changelog diff engine — compare changelogs between releases."""
from __future__ import annotations


def parse_changelog(entries: list[dict]) -> dict:
    by_type: dict[str, list[str]] = {}
    for e in entries:
        t = e.get("type", "other")
        by_type.setdefault(t, []).append(e.get("description", ""))
    breaking = [e for e in entries if e.get("breaking", False)]
    return {"entries": entries, "total": len(entries), "by_type": by_type,
            "breaking_count": len(breaking), "has_breaking": len(breaking) > 0,
            "type_count": len(by_type)}


def diff_changelogs(old: list[dict], new: list[dict]) -> dict:
    old_descs = {e.get("description", "") for e in old}
    new_descs = {e.get("description", "") for e in new}
    added = [e for e in new if e.get("description", "") not in old_descs]
    removed = [e for e in old if e.get("description", "") not in new_descs]
    return {"added": added, "removed": removed,
            "added_count": len(added), "removed_count": len(removed),
            "net_change": len(added) - len(removed)}
