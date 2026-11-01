"""Versioned Config — version-controlled configuration management for extensions.

Stores config snapshots with version history, diff generation between
versions, rollback, and JSON Schema validation per config key.
"""
from __future__ import annotations
import copy
import json
import secrets
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone


@dataclass
class ConfigVersion:
    version: int
    data: dict
    author: str
    message: str = ""
    created_at: str = ""

    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now(timezone.utc).isoformat()


class VersionedConfigService:
    """Manages versioned configuration with diff and rollback."""

    def __init__(self):
        self._configs: dict[str, list[ConfigVersion]] = defaultdict(list)
        self._schemas: dict[str, dict] = {}

    def set_schema(self, extension_id: str, schema: dict) -> None:
        self._schemas[extension_id] = schema

    def _validate(self, extension_id: str, data: dict) -> list[str]:
        schema = self._schemas.get(extension_id)
        if not schema:
            return []
        errors = []
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        for key in required:
            if key not in data:
                errors.append(f"Missing required key: {key}")
        for key, value in data.items():
            if key in properties:
                expected_type = properties[key].get("type")
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"{key}: expected string")
                elif expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"{key}: expected integer")
                elif expected_type == "boolean" and not isinstance(value, bool):
                    errors.append(f"{key}: expected boolean")
        return errors

    def save(self, extension_id: str, data: dict, author: str,
             message: str = "") -> ConfigVersion | dict:
        errors = self._validate(extension_id, data)
        if errors:
            return {"error": "Validation failed", "details": errors}

        versions = self._configs[extension_id]
        version_num = len(versions) + 1
        cv = ConfigVersion(
            version=version_num, data=copy.deepcopy(data),
            author=author, message=message,
        )
        versions.append(cv)
        return cv

    def get_current(self, extension_id: str) -> dict | None:
        versions = self._configs.get(extension_id, [])
        return versions[-1].data if versions else None

    def get_version(self, extension_id: str, version: int) -> ConfigVersion | None:
        versions = self._configs.get(extension_id, [])
        if 1 <= version <= len(versions):
            return versions[version - 1]
        return None

    def diff(self, extension_id: str, v1: int, v2: int) -> dict:
        cv1 = self.get_version(extension_id, v1)
        cv2 = self.get_version(extension_id, v2)
        if not cv1 or not cv2:
            return {"error": "Version not found"}

        added = {k: cv2.data[k] for k in cv2.data if k not in cv1.data}
        removed = {k: cv1.data[k] for k in cv1.data if k not in cv2.data}
        changed = {k: {"from": cv1.data[k], "to": cv2.data[k]}
                   for k in cv1.data if k in cv2.data and cv1.data[k] != cv2.data[k]}

        return {"added": added, "removed": removed, "changed": changed,
                "has_changes": bool(added or removed or changed)}

    def rollback(self, extension_id: str, version: int,
                 author: str) -> ConfigVersion | dict:
        cv = self.get_version(extension_id, version)
        if not cv:
            return {"error": "Version not found"}
        return self.save(extension_id, cv.data, author,
                         f"Rollback to v{version}")

    def get_history(self, extension_id: str) -> list[ConfigVersion]:
        return list(self._configs.get(extension_id, []))
