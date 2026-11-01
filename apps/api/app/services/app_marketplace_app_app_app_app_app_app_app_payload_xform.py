"""Webhook payload transformer — transform payloads between formats."""
from __future__ import annotations
import html


def transform_payload(payload: dict, mapping: dict[str, str]) -> dict:
    result = {}
    for target_key, source_path in mapping.items():
        parts = source_path.split(".")
        value = payload
        for part in parts:
            if isinstance(value, dict):
                value = value.get(part)
            else:
                value = None
                break
        result[target_key] = value
    return {"transformed": result, "mapped_fields": len(mapping),
            "null_fields": sum(1 for v in result.values() if v is None)}


def flatten_payload(payload: dict, prefix: str = "") -> dict:
    flat = {}
    for k, v in payload.items():
        key = f"{prefix}.{k}" if prefix else k
        if isinstance(v, dict):
            flat.update(flatten_payload(v, key))
        else:
            flat[key] = v
    return flat


def redact_fields(payload: dict, fields: list[str]) -> dict:
    result = {}
    redacted = 0
    for k, v in payload.items():
        if k in fields:
            result[k] = "[REDACTED]"
            redacted += 1
        elif isinstance(v, dict):
            inner = redact_fields(v, fields)
            result[k] = inner["payload"]
            redacted += inner["redacted"]
        else:
            result[k] = v
    return {"payload": result, "redacted": redacted}
