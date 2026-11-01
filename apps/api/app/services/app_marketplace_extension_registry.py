"""Extension Registry — manage extension packages in the marketplace.

Provides registration, discovery, and version management for
developer-built extensions that plug into the OpenSkill platform.
"""
from __future__ import annotations
from datetime import datetime, timezone


_extensions: dict[str, dict] = {}


def register_extension(
    extension_id: str,
    name: str,
    version: str,
    author: str,
    description: str = "",
    entry_point: str = "index",
    permissions: list[str] | None = None,
) -> dict:
    """Register a new extension or update an existing one."""
    now = datetime.now(timezone.utc).isoformat()
    ext = {
        "extension_id": extension_id,
        "name": name,
        "version": version,
        "author": author,
        "description": description,
        "entry_point": entry_point,
        "permissions": permissions or [],
        "registered_at": now,
        "updated_at": now,
        "status": "active",
        "downloads": 0,
    }
    _extensions[extension_id] = ext
    return ext


def get_extension(extension_id: str) -> dict | None:
    """Look up an extension by ID."""
    return _extensions.get(extension_id)


def list_extensions(author: str | None = None, status: str = "active") -> list[dict]:
    """List extensions, optionally filtered by author and status."""
    results = list(_extensions.values())
    if author:
        results = [e for e in results if e["author"] == author]
    results = [e for e in results if e["status"] == status]
    return sorted(results, key=lambda e: e["name"])


def deprecate_extension(extension_id: str) -> dict | None:
    """Mark an extension as deprecated."""
    ext = _extensions.get(extension_id)
    if ext:
        ext["status"] = "deprecated"
        ext["updated_at"] = datetime.now(timezone.utc).isoformat()
    return ext


def search_extensions(query: str) -> list[dict]:
    """Search extensions by name or description."""
    q = query.lower()
    return [
        e for e in _extensions.values()
        if q in e["name"].lower() or q in e["description"].lower()
    ]
