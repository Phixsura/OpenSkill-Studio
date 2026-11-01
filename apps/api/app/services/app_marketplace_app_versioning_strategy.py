"""Versioning strategy — semver validation, auto-increment, compatibility checks."""

import re

SEMVER_RE = re.compile(r'^(\d+)\.(\d+)\.(\d+)(?:-([\w.]+))?(?:\+[\w.]+)?$')


def parse_semver(version: str) -> dict | None:
    m = SEMVER_RE.match(version)
    if not m:
        return None
    return {"major": int(m.group(1)), "minor": int(m.group(2)), "patch": int(m.group(3)),
            "prerelease": m.group(4)}


def suggest_next_version(*, current: str, change_type: str) -> dict:
    parsed = parse_semver(current)
    if not parsed:
        return {"error": f"Invalid semver: {current}"}
    if change_type == "major":
        return {"version": f"{parsed['major'] + 1}.0.0", "error": None}
    elif change_type == "minor":
        return {"version": f"{parsed['major']}.{parsed['minor'] + 1}.0", "error": None}
    elif change_type == "patch":
        return {"version": f"{parsed['major']}.{parsed['minor']}.{parsed['patch'] + 1}", "error": None}
    return {"error": f"Invalid change type: {change_type}"}


def check_version_order(*, current: str, proposed: str) -> dict:
    cur = parse_semver(current)
    prop = parse_semver(proposed)
    if not cur or not prop:
        return {"valid": False, "error": "Invalid version format"}
    cur_tuple = (cur["major"], cur["minor"], cur["patch"])
    prop_tuple = (prop["major"], prop["minor"], prop["patch"])
    is_higher = prop_tuple > cur_tuple
    return {"valid": is_higher, "error": None if is_higher else "Proposed version must be higher than current"}


def detect_breaking_change(*, old_version: str, new_version: str) -> bool:
    old = parse_semver(old_version)
    new = parse_semver(new_version)
    if not old or not new:
        return False
    return new["major"] > old["major"]
