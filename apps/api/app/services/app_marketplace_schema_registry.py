"""Schema Registry — manage and validate JSON schemas for extension APIs.

Provides schema registration, versioning, validation, and compatibility
checking for extension data contracts.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timezone
from copy import deepcopy


@dataclass
class SchemaVersion:
    version: int
    schema: dict
    registered_at: str = ""
    deprecated: bool = False

    def __post_init__(self):
        if not self.registered_at:
            self.registered_at = datetime.now(timezone.utc).isoformat()


class SchemaRegistry:
    """Manages versioned JSON schemas for extension APIs."""

    def __init__(self):
        self._schemas: dict[str, list[SchemaVersion]] = {}  # subject -> versions

    def register(self, subject: str, schema: dict) -> SchemaVersion:
        """Register a new schema version for a subject."""
        versions = self._schemas.setdefault(subject, [])
        version_num = len(versions) + 1
        sv = SchemaVersion(version=version_num, schema=deepcopy(schema))
        versions.append(sv)
        return sv

    def get_latest(self, subject: str) -> SchemaVersion | None:
        versions = self._schemas.get(subject, [])
        active = [v for v in versions if not v.deprecated]
        return active[-1] if active else None

    def get_version(self, subject: str, version: int) -> SchemaVersion | None:
        versions = self._schemas.get(subject, [])
        for v in versions:
            if v.version == version:
                return v
        return None

    def list_versions(self, subject: str) -> list[SchemaVersion]:
        return list(self._schemas.get(subject, []))

    def list_subjects(self) -> list[str]:
        return sorted(self._schemas.keys())

    def deprecate_version(self, subject: str, version: int) -> bool:
        sv = self.get_version(subject, version)
        if sv:
            sv.deprecated = True
            return True
        return False

    def validate(self, subject: str, data: dict, version: int | None = None) -> tuple[bool, list[str]]:
        """Validate data against a schema. Basic type/required checking."""
        sv = self.get_version(subject, version) if version else self.get_latest(subject)
        if not sv:
            return False, [f"No schema found for {subject}"]

        schema = sv.schema
        errors = []

        # Check required fields
        required = schema.get("required", [])
        for field_name in required:
            if field_name not in data:
                errors.append(f"Missing required field: {field_name}")

        # Check field types
        properties = schema.get("properties", {})
        for field_name, field_def in properties.items():
            if field_name not in data:
                continue
            expected_type = field_def.get("type", "")
            value = data[field_name]
            type_map = {"string": str, "integer": int, "number": (int, float),
                        "boolean": bool, "array": list, "object": dict}
            expected = type_map.get(expected_type)
            if expected and not isinstance(value, expected):
                errors.append(f"Field '{field_name}': expected {expected_type}, got {type(value).__name__}")

        return len(errors) == 0, errors

    def check_compatibility(self, subject: str, new_schema: dict) -> tuple[bool, list[str]]:
        """Check if new schema is backward-compatible with latest."""
        latest = self.get_latest(subject)
        if not latest:
            return True, []

        issues = []
        old_required = set(latest.schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        added_required = new_required - old_required
        if added_required:
            issues.append(f"New required fields (breaking): {', '.join(added_required)}")

        old_props = set(latest.schema.get("properties", {}).keys())
        new_props = set(new_schema.get("properties", {}).keys())
        removed = old_props - new_props
        if removed:
            issues.append(f"Removed fields (breaking): {', '.join(removed)}")

        return len(issues) == 0, issues
