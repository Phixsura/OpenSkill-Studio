"""App version diff service — compare two manifest versions.

Produces a human-readable diff report showing what changed
between two versions of an app manifest.
"""

import structlog

log = structlog.get_logger()


def diff_manifests(old: dict, new: dict) -> dict:
    """Compare two manifests and return a structured diff.

    Returns:
        {
            "permissions": {"added": [...], "removed": [...]},
            "sandbox": {"changed": bool, "details": {...}},
            "events": {"added": [...], "removed": [...]},
            "ui_extensions": {"added": [...], "removed": [...]},
            "secrets": {"added": [...], "removed": [...]},
            "config_schema_changed": bool,
            "breaking": bool,
            "summary": str,
        }
    """
    result = {
        "permissions": _diff_lists(
            old.get("permissions", []),
            new.get("permissions", []),
        ),
        "events": _diff_lists(
            old.get("event_subscriptions", []),
            new.get("event_subscriptions", []),
        ),
        "secrets": _diff_secrets(
            old.get("secrets", []),
            new.get("secrets", []),
        ),
        "ui_extensions": _diff_extensions(
            old.get("ui_extensions", []),
            new.get("ui_extensions", []),
        ),
        "sandbox": _diff_sandbox(
            old.get("sandbox"),
            new.get("sandbox"),
        ),
        "config_schema_changed": old.get("config_schema") != new.get("config_schema"),
        "version_from": old.get("app", {}).get("version", "unknown"),
        "version_to": new.get("app", {}).get("version", "unknown"),
    }

    # Determine if breaking
    result["breaking"] = bool(result["permissions"]["removed"])
    result["summary"] = _build_summary(result)

    return result


def _diff_lists(old: list, new: list) -> dict:
    old_set = set(old)
    new_set = set(new)
    return {
        "added": sorted(new_set - old_set),
        "removed": sorted(old_set - new_set),
        "unchanged": sorted(old_set & new_set),
    }


def _diff_secrets(old: list[dict], new: list[dict]) -> dict:
    old_keys = {s.get("key") for s in old}
    new_keys = {s.get("key") for s in new}
    return {
        "added": sorted(new_keys - old_keys),
        "removed": sorted(old_keys - new_keys),
    }


def _diff_extensions(old: list[dict], new: list[dict]) -> dict:
    old_surfaces = {e.get("surface") for e in old}
    new_surfaces = {e.get("surface") for e in new}
    return {
        "added": sorted(new_surfaces - old_surfaces),
        "removed": sorted(old_surfaces - new_surfaces),
    }


def _diff_sandbox(old: dict | None, new: dict | None) -> dict:
    if old is None and new is None:
        return {"changed": False}
    if old is None or new is None:
        return {"changed": True, "details": "sandbox added or removed"}

    changes = {}
    for key in ["runtime", "memory_mb", "timeout_seconds"]:
        if old.get(key) != new.get(key):
            changes[key] = {"from": old.get(key), "to": new.get(key)}

    return {"changed": bool(changes), "details": changes}


def _build_summary(result: dict) -> str:
    parts = []
    pa = len(result["permissions"]["added"])
    pr = len(result["permissions"]["removed"])
    if pa:
        parts.append(f"+{pa} permissions")
    if pr:
        parts.append(f"-{pr} permissions (BREAKING)")
    ea = len(result["events"]["added"])
    if ea:
        parts.append(f"+{ea} event subscriptions")
    sa = len(result["secrets"]["added"])
    if sa:
        parts.append(f"+{sa} secrets")
    if result["sandbox"]["changed"]:
        parts.append("sandbox config changed")
    if result["config_schema_changed"]:
        parts.append("config schema changed")
    return "; ".join(parts) if parts else "No changes"
