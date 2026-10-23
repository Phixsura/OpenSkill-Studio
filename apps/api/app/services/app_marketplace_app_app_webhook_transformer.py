"""Webhook transformer — payload transformation templates."""

import html
import json
import re


def apply_template(*, template: dict, payload: dict) -> dict:
    def resolve(value, data):
        if isinstance(value, str) and value.startswith("{{") and value.endswith("}}"):
            path = value[2:-2].strip()
            return _get_nested(data, path)
        if isinstance(value, dict):
            return {k: resolve(v, data) for k, v in value.items()}
        if isinstance(value, list):
            return [resolve(v, data) for v in value]
        return value

    result = resolve(template, payload)
    return {"transformed": result, "original_keys": list(payload.keys()),
            "output_keys": list(result.keys()) if isinstance(result, dict) else []}


def _get_nested(data: dict, path: str):
    parts = path.split(".")
    current = data
    for p in parts:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current


def validate_template(*, template: dict) -> dict:
    placeholders = []
    _find_placeholders(template, placeholders)
    return {"valid": True, "placeholders": placeholders, "count": len(placeholders)}


def _find_placeholders(obj, result: list, prefix: str = ""):
    if isinstance(obj, str) and "{{" in obj:
        m = re.findall(r"\{\{\s*(.+?)\s*\}\}", obj)
        result.extend(m)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _find_placeholders(v, result)
    elif isinstance(obj, list):
        for v in obj:
            _find_placeholders(v, result)
