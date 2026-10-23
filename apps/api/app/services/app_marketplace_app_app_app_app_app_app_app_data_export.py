"""Data export manager — generate and track data exports."""
from __future__ import annotations
import hashlib
import time

_exports: list[dict] = []


def create_export(name: str, format: str, filters: dict | None = None,
                  row_count: int = 0) -> dict:
    valid_formats = {"csv", "json", "xlsx", "parquet"}
    if format not in valid_formats:
        return {"created": False, "error": f"invalid format, use {sorted(valid_formats)}"}
    export_id = hashlib.sha256(f"{name}:{time.time()}".encode()).hexdigest()[:10]
    entry = {"id": export_id, "name": name, "format": format,
             "filters": filters or {}, "row_count": row_count,
             "status": "completed", "created_at": time.time(),
             "size_mb": round(row_count * 0.001, 2)}
    _exports.append(entry)
    return {"created": True, **entry}


def list_exports(limit: int = 20) -> list[dict]:
    return list(reversed(_exports[-limit:]))


def export_stats() -> dict:
    total_size = sum(e["size_mb"] for e in _exports)
    by_format: dict[str, int] = {}
    for e in _exports:
        by_format[e["format"]] = by_format.get(e["format"], 0) + 1
    return {"total": len(_exports), "total_size_mb": round(total_size, 2),
            "by_format": by_format}


def clear_exports() -> None:
    _exports.clear()
