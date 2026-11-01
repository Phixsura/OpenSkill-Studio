"""Dynamic config flags — runtime toggleable configuration."""
from __future__ import annotations

_flags: dict[str, dict] = {}


def set_flag(key: str, value: object, description: str = "", owner: str = "") -> dict:
    _flags[key] = {"key": key, "value": value, "description": description,
                    "owner": owner, "type": type(value).__name__}
    return _flags[key]


def get_flag(key: str, default: object = None) -> object:
    entry = _flags.get(key)
    return entry["value"] if entry else default


def list_flags(owner: str | None = None) -> list[dict]:
    items = list(_flags.values())
    if owner:
        items = [f for f in items if f["owner"] == owner]
    return items


def bulk_update(updates: dict[str, object]) -> dict:
    updated = 0
    for k, v in updates.items():
        if k in _flags:
            _flags[k]["value"] = v
            _flags[k]["type"] = type(v).__name__
            updated += 1
    return {"updated": updated, "total_requested": len(updates)}


def clear_flags() -> None:
    _flags.clear()
