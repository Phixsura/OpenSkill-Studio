"""Consumer API Endpoint Versioned Schema — manage schema evolution per endpoint version."""
from __future__ import annotations
from dataclasses import dataclass, field
import structlog

log = structlog.get_logger()

@dataclass
class SchemaVersion:
    version: str
    endpoint_path: str
    fields: dict[str, str] = field(default_factory=dict)  # field_name -> type
    required_fields: list[str] = field(default_factory=list)
    deprecated_fields: list[str] = field(default_factory=list)
    added_in: str = ""  # version when field was added
    changelog: str = ""

@dataclass
class SchemaCompat:
    from_version: str
    to_version: str
    added_fields: list[str] = field(default_factory=list)
    removed_fields: list[str] = field(default_factory=list)
    type_changes: dict[str, tuple[str, str]] = field(default_factory=dict)  # field -> (old, new)
    breaking: bool = False

class AppAPIDeveloperPlatformSDKApiPlatformDeveloperApiApiConsumerApiApiConsumerApiConsumerApiEndpointVersionedSchema:
    def __init__(self) -> None:
        self._schemas: dict[tuple[str, str, str], SchemaVersion] = {}  # (inst, path, version)

    def register(self, installation_id: str, schema: SchemaVersion) -> SchemaVersion:
        if not installation_id:
            raise ValueError("installation_id is required")
        key = (installation_id, schema.endpoint_path, schema.version)
        self._schemas[key] = schema
        return schema

    def get(self, installation_id: str, endpoint_path: str, version: str) -> SchemaVersion | None:
        return self._schemas.get((installation_id, endpoint_path, version))

    def compare(self, installation_id: str, endpoint_path: str, from_version: str, to_version: str) -> SchemaCompat:
        old = self._schemas.get((installation_id, endpoint_path, from_version))
        new = self._schemas.get((installation_id, endpoint_path, to_version))
        if not old or not new:
            raise ValueError("Both versions must exist")
        old_fields = set(old.fields.keys())
        new_fields = set(new.fields.keys())
        added = sorted(new_fields - old_fields)
        removed = sorted(old_fields - new_fields)
        type_changes: dict[str, tuple[str, str]] = {}
        for f in old_fields & new_fields:
            if old.fields[f] != new.fields[f]:
                type_changes[f] = (old.fields[f], new.fields[f])
        # Breaking if required fields removed or types changed
        breaking = bool(removed) or bool(type_changes) or any(f in new.required_fields for f in added if f not in old.fields)
        return SchemaCompat(from_version=from_version, to_version=to_version, added_fields=added, removed_fields=removed, type_changes=type_changes, breaking=breaking)

    def list_versions(self, installation_id: str, endpoint_path: str) -> list[SchemaVersion]:
        return sorted([s for (inst, p, _), s in self._schemas.items() if inst == installation_id and p == endpoint_path], key=lambda s: s.version)
