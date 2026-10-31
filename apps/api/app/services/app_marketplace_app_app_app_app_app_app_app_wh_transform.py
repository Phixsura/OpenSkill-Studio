"""Webhook payload transformer — transform payloads between formats."""
from __future__ import annotations
import html


def transform_payload(payload: dict, mapping: dict[str, str]) -> dict:
    result = {}
    for target_key, source_path in mapping.items():
        value = payload
        for part in source_path.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        if value is not None:
            result[target_key] = value
    return {"transformed": result, "fields_mapped": len(result),
            "fields_missing": len(mapping) - len(result)}


def sanitize_payload(payload: dict) -> dict:
    sanitized = {}
    for k, v in payload.items():
        if isinstance(v, str):
            sanitized[k] = html.escape(v)
        elif isinstance(v, dict):
            sanitized[k] = sanitize_payload(v)["data"]
        else:
            sanitized[k] = v
    return {"data": sanitized, "fields_sanitized": len(sanitized)}
