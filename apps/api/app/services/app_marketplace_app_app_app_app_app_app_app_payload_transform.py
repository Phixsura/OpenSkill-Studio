"""Payload transformer — map, filter, and transform webhook/API payloads."""
from __future__ import annotations
import copy


def apply_mapping(payload: dict, mapping: dict) -> dict:
    result = {}
    for target_key, source_path in mapping.items():
        value = _get_path(payload, source_path)
        if value is not None:
            _set_path(result, target_key, value)
    return result


def apply_filter(payload: dict, *, include: list[str] | None = None,
                  exclude: list[str] | None = None) -> dict:
    result = copy.deepcopy(payload)
    if include:
        result = {k: v for k, v in result.items() if k in include}
    if exclude:
        result = {k: v for k, v in result.items() if k not in exclude}
    return result


def apply_template(template: str, payload: dict) -> str:
    result = template
    for key, value in _flatten(payload).items():
        result = result.replace(f"{{{{{key}}}}}", str(value))
    return result


def _get_path(data: dict, path: str):
    parts = path.split(".")
    current = data
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def _set_path(data: dict, path: str, value) -> None:
    parts = path.split(".")
    current = data
    for p in parts[:-1]:
        current = current.setdefault(p, {})
    current[parts[-1]] = value


def _flatten(data: dict, prefix: str = "") -> dict:
    result = {}
    for k, v in data.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            result.update(_flatten(v, key))
        else:
            result[key] = v
    return result
