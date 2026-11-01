"""Webhook payload inspector — analyze and display webhook payloads."""
from __future__ import annotations
import json


def inspect_payload(payload: dict) -> dict:
    serialized = json.dumps(payload, indent=2)
    size = len(serialized.encode())
    depth = _max_depth(payload)
    field_count = _count_fields(payload)
    return {
        "size_bytes": size, "size_display": f"{size} B" if size < 1024 else f"{size / 1024:.1f} KB",
        "depth": depth, "field_count": field_count,
        "fields": list(payload.keys()),
        "formatted": serialized,
        "warnings": _check_warnings(payload, size, depth),
    }


def _max_depth(obj: dict, current: int = 0) -> int:
    if not isinstance(obj, dict):
        return current
    if not obj:
        return current + 1
    return max(_max_depth(v, current + 1) for v in obj.values())


def _count_fields(obj: dict) -> int:
    count = len(obj)
    for v in obj.values():
        if isinstance(v, dict):
            count += _count_fields(v)
    return count


def _check_warnings(payload: dict, size: int, depth: int) -> list[str]:
    warnings = []
    if size > 64 * 1024:
        warnings.append("Payload exceeds 64KB — may be rejected by some endpoints")
    if depth > 10:
        warnings.append("Deep nesting detected — consider flattening")
    return warnings
