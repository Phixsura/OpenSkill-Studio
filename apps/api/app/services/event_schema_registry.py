"""Event Schema Registry — versioned event schemas for the developer platform webhook/event system.

Manages the canonical event type catalog for ADR-016 Part F:
- Register and version event schemas (JSON Schema)
- Validate event payloads against registered schemas
- Schema evolution rules (backward compatibility checks)
- Event type discovery for developer documentation
- Deprecation tracking with sunset dates
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum

import structlog

log = structlog.get_logger()

EVENT_TYPE_PATTERN = re.compile(r"^[a-z][a-z0-9_]*\.[a-z][a-z0-9_]*$")


class SchemaStatus(str, Enum):
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    RETIRED = "retired"


class CompatibilityResult(str, Enum):
    COMPATIBLE = "compatible"
    BREAKING = "breaking"
    UNKNOWN = "unknown"


@dataclass
class EventSchema:
    """A versioned event schema definition."""

    event_type: str          # e.g. "skill_pack.published"
    version: int             # monotonically increasing
    schema: dict             # JSON Schema object
    description: str
    status: SchemaStatus = SchemaStatus.ACTIVE
    deprecated_at: datetime | None = None
    sunset_at: datetime | None = None
    deprecation_message: str | None = None
    example_payload: dict | None = None
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ValidationResult:
    """Result of validating an event payload against a schema."""

    valid: bool
    errors: list[str]
    event_type: str
    schema_version: int


@dataclass
class CompatibilityReport:
    """Report on backward compatibility between schema versions."""

    event_type: str
    old_version: int
    new_version: int
    result: CompatibilityResult
    breaking_changes: list[str]
    additions: list[str]


class EventSchemaRegistry:
    """In-memory event schema registry with versioning and validation."""

    def __init__(self):
        # (event_type, version) → EventSchema
        self._schemas: dict[tuple[str, int], EventSchema] = {}
        # event_type → latest version number
        self._latest: dict[str, int] = {}

    # ── Registration ─────────────────────────────────────

    def register(self, event_type: str, schema: dict,
                 description: str, example_payload: dict | None = None) -> EventSchema:
        """Register a new version of an event schema.

        Version is auto-incremented. Raises ValueError for invalid event types.
        """
        if not EVENT_TYPE_PATTERN.match(event_type):
            raise ValueError(
                f"Invalid event_type '{event_type}': must be 'resource.action' "
                f"(lowercase, underscores allowed)"
            )

        if not isinstance(schema, dict) or "type" not in schema:
            raise ValueError("Schema must be a JSON Schema object with a 'type' field")

        version = self._latest.get(event_type, 0) + 1
        entry = EventSchema(
            event_type=event_type,
            version=version,
            schema=schema,
            description=description,
            example_payload=example_payload,
        )
        self._schemas[(event_type, version)] = entry
        self._latest[event_type] = version

        log.info(
            "event_schema.registered",
            event_type=event_type,
            version=version,
        )
        return entry

    def deprecate(self, event_type: str, version: int | None = None,
                  message: str | None = None,
                  sunset_at: datetime | None = None) -> EventSchema:
        """Mark a schema version (or latest) as deprecated."""
        v = version or self._latest.get(event_type, 0)
        entry = self._schemas.get((event_type, v))
        if entry is None:
            raise ValueError(f"Schema not found: {event_type} v{v}")

        entry.status = SchemaStatus.DEPRECATED
        entry.deprecated_at = datetime.now(UTC)
        entry.deprecation_message = message
        entry.sunset_at = sunset_at

        log.info("event_schema.deprecated", event_type=event_type, version=v)
        return entry

    def retire(self, event_type: str, version: int) -> EventSchema:
        """Mark a schema version as retired (no longer accepted)."""
        entry = self._schemas.get((event_type, version))
        if entry is None:
            raise ValueError(f"Schema not found: {event_type} v{version}")
        entry.status = SchemaStatus.RETIRED
        return entry

    # ── Querying ─────────────────────────────────────────

    def get(self, event_type: str, version: int | None = None) -> EventSchema | None:
        """Get a specific version or latest."""
        v = version or self._latest.get(event_type, 0)
        return self._schemas.get((event_type, v))

    def get_latest_version(self, event_type: str) -> int:
        return self._latest.get(event_type, 0)

    def list_event_types(self, status: SchemaStatus | None = None) -> list[EventSchema]:
        """List latest version of all registered event types."""
        result = []
        for event_type, version in self._latest.items():
            entry = self._schemas[(event_type, version)]
            if status is None or entry.status == status:
                result.append(entry)
        return sorted(result, key=lambda e: e.event_type)

    def list_versions(self, event_type: str) -> list[EventSchema]:
        """List all versions of a specific event type."""
        versions = []
        for (et, v), entry in self._schemas.items():
            if et == event_type:
                versions.append(entry)
        return sorted(versions, key=lambda e: e.version)

    # ── Validation ───────────────────────────────────────

    def validate(self, event_type: str, payload: dict,
                 version: int | None = None) -> ValidationResult:
        """Validate an event payload against its schema.

        Uses a simplified validation (type checks on required fields).
        Production should use jsonschema library.
        """
        v = version or self._latest.get(event_type, 0)
        entry = self._schemas.get((event_type, v))

        if entry is None:
            return ValidationResult(
                valid=False,
                errors=[f"No schema found for {event_type} v{v}"],
                event_type=event_type,
                schema_version=v,
            )

        if entry.status == SchemaStatus.RETIRED:
            return ValidationResult(
                valid=False,
                errors=[f"Schema {event_type} v{v} is retired"],
                event_type=event_type,
                schema_version=v,
            )

        errors = self._validate_against_schema(payload, entry.schema)

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            event_type=event_type,
            schema_version=v,
        )

    # ── Compatibility ────────────────────────────────────

    def check_compatibility(self, event_type: str,
                            new_schema: dict) -> CompatibilityReport:
        """Check if a new schema is backward-compatible with the latest version."""
        latest_v = self._latest.get(event_type, 0)
        if latest_v == 0:
            return CompatibilityReport(
                event_type=event_type,
                old_version=0,
                new_version=1,
                result=CompatibilityResult.COMPATIBLE,
                breaking_changes=[],
                additions=[],
            )

        old = self._schemas[(event_type, latest_v)]
        breaking = []
        additions = []

        old_required = set(old.schema.get("required", []))
        new_required = set(new_schema.get("required", []))
        old_props = set(old.schema.get("properties", {}).keys())
        new_props = set(new_schema.get("properties", {}).keys())

        # New required fields = breaking (old producers don't send them)
        added_required = new_required - old_required
        if added_required:
            breaking.append(f"New required fields: {', '.join(sorted(added_required))}")

        # Removed properties = breaking (consumers may depend on them)
        removed = old_props - new_props
        if removed:
            breaking.append(f"Removed properties: {', '.join(sorted(removed))}")

        # New optional properties = compatible addition
        added_props = new_props - old_props
        if added_props:
            additions.append(f"New properties: {', '.join(sorted(added_props))}")

        result = CompatibilityResult.BREAKING if breaking else CompatibilityResult.COMPATIBLE

        return CompatibilityReport(
            event_type=event_type,
            old_version=latest_v,
            new_version=latest_v + 1,
            result=result,
            breaking_changes=breaking,
            additions=additions,
        )

    # ── Internal ─────────────────────────────────────────

    @staticmethod
    def _validate_against_schema(payload: dict, schema: dict) -> list[str]:
        """Simplified schema validation (required fields + type checks)."""
        errors = []

        if schema.get("type") == "object" and not isinstance(payload, dict):
            errors.append(f"Expected object, got {type(payload).__name__}")
            return errors

        required = schema.get("required", [])
        properties = schema.get("properties", {})

        for field_name in required:
            if field_name not in payload:
                errors.append(f"Missing required field: {field_name}")

        for field_name, value in payload.items():
            if field_name in properties:
                expected_type = properties[field_name].get("type")
                if expected_type and not _type_matches(value, expected_type):
                    errors.append(
                        f"Field '{field_name}': expected {expected_type}, "
                        f"got {type(value).__name__}"
                    )

        return errors


def _type_matches(value: object, json_type: str) -> bool:
    """Check if a Python value matches a JSON Schema type."""
    type_map = {
        "string": str,
        "integer": int,
        "number": (int, float),
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    expected = type_map.get(json_type)
    if expected is None:
        return True  # Unknown type → don't reject
    # In JSON, booleans are not numbers
    if json_type in ("integer", "number") and isinstance(value, bool):
        return False
    return isinstance(value, expected)
