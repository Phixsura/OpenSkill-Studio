"""Clipboard helper — format values for copy-to-clipboard with redaction."""
from __future__ import annotations
import html


def format_for_copy(*, value: str, label: str = "", sensitive: bool = False,
                      max_length: int = 5000) -> dict:
    truncated = len(value) > max_length
    safe_value = value[:max_length]
    display = _mask(safe_value) if sensitive else safe_value
    return {
        "value": safe_value, "display": display,
        "label": html.escape(label), "sensitive": sensitive,
        "truncated": truncated, "length": len(safe_value),
        "copy_text": safe_value,
    }


def build_copy_items(items: list[dict]) -> list[dict]:
    return [format_for_copy(value=i.get("value", ""), label=i.get("label", ""),
                             sensitive=i.get("sensitive", False))
            for i in items]


def _mask(val: str) -> str:
    if len(val) <= 8:
        return "••••••••"
    return val[:4] + "•" * (len(val) - 8) + val[-4:]
