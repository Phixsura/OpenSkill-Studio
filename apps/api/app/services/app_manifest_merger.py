"""Manifest merger — merge partial manifest updates into existing manifests."""

import copy


def merge_manifests(base: dict, updates: dict) -> dict:
    """Deep merge updates into base manifest."""
    result = copy.deepcopy(base)
    for key, value in updates.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_manifests(result[key], value)
        elif key in result and isinstance(result[key], list) and isinstance(value, list):
            result[key] = value  # Replace lists entirely
        else:
            result[key] = copy.deepcopy(value)
    return result


def patch_manifest(manifest: dict, patches: list[dict]) -> dict:
    """Apply a list of patches to a manifest.
    Each patch: {"op": "set|delete|append", "path": "dot.path", "value": ...}
    """
    result = copy.deepcopy(manifest)
    for patch in patches:
        op = patch.get("op", "set")
        path_parts = patch.get("path", "").split(".")
        value = patch.get("value")

        if op == "delete":
            _delete_path(result, path_parts)
        elif op == "append":
            target = _get_path(result, path_parts)
            if isinstance(target, list):
                target.append(value)
        else:  # set
            _set_path(result, path_parts, value)
    return result


def _get_path(obj: dict, parts: list[str]):
    for part in parts:
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
    return obj


def _set_path(obj: dict, parts: list[str], value) -> None:
    for part in parts[:-1]:
        if part not in obj or not isinstance(obj[part], dict):
            obj[part] = {}
        obj = obj[part]
    obj[parts[-1]] = value


def _delete_path(obj: dict, parts: list[str]) -> None:
    for part in parts[:-1]:
        if isinstance(obj, dict):
            obj = obj.get(part, {})
    if isinstance(obj, dict):
        obj.pop(parts[-1], None)
