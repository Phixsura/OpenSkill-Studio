"""Config Schema Registry — register and validate extension config schemas.

Manages JSON Schema definitions for extension configurations, validates
config values against schemas, supports schema versioning and migration.
"""
from __future__ import annotations
import json
import secrets
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class ConfigSchema:
    schema_id: str
    extension_id: str
    version: int
    fields: list[dict]  # [{name, type, required, default, description, enum}]
    created_at: str = ""


TYPE_VALIDATORS = {
    "string": lambda v: isinstance(v, str),
    "integer": lambda v: isinstance(v, int) and not isinstance(v, bool),
    "number": lambda v: isinstance(v, (int, float)) and not isinstance(v, bool),
    "boolean": lambda v: isinstance(v, bool),
    "array": lambda v: isinstance(v, list),
    "object": lambda v: isinstance(v, dict),
}


class ConfigSchemaRegistryService:
    """Registers schemas and validates configs against them."""

    def __init__(self):
        self._schemas: dict[str, list[ConfigSchema]] = defaultdict(list)

    def register(self, extension_id: str,
                 fields: list[dict]) -> ConfigSchema:
        # Validate field definitions
        for f in fields:
            if "name" not in f or "type" not in f:
                raise ValueError("Each field must have 'name' and 'type'")
            if f["type"] not in TYPE_VALIDATORS:
                raise ValueError(f"Invalid type: {f['type']}")

        versions = self._schemas[extension_id]
        version = len(versions) + 1
        schema = ConfigSchema(
            schema_id=f"cs_{secrets.token_urlsafe(8)}",
            extension_id=extension_id, version=version,
            fields=fields,
        )
        versions.append(schema)
        return schema

    def get_latest(self, extension_id: str) -> ConfigSchema | None:
        versions = self._schemas.get(extension_id, [])
        return versions[-1] if versions else None

    def get_version(self, extension_id: str, version: int) -> ConfigSchema | None:
        versions = self._schemas.get(extension_id, [])
        if 1 <= version <= len(versions):
            return versions[version - 1]
        return None

    def validate(self, extension_id: str, config: dict,
                 version: int | None = None) -> dict:
        schema = (self.get_version(extension_id, version) if version
                  else self.get_latest(extension_id))
        if not schema:
            return {"valid": False, "errors": ["No schema found"]}

        errors: list[str] = []
        defaults_applied: dict = {}

        field_map = {f["name"]: f for f in schema.fields}

        # Check required fields
        for f in schema.fields:
            if f.get("required", False) and f["name"] not in config:
                if "default" in f:
                    defaults_applied[f["name"]] = f["default"]
                else:
                    errors.append(f"Missing required: {f['name']}")

        # Check types and enum
        for key, value in config.items():
            if key not in field_map:
                continue  # unknown fields allowed
            f = field_map[key]
            validator = TYPE_VALIDATORS.get(f["type"])
            if validator and not validator(value):
                errors.append(f"{key}: expected {f['type']}, got {type(value).__name__}")
            if "enum" in f and value not in f["enum"]:
                errors.append(f"{key}: must be one of {f['enum']}")

        return {
            "valid": len(errors) == 0, "errors": errors,
            "defaults_applied": defaults_applied,
            "schema_version": schema.version,
        }

    def diff_versions(self, extension_id: str, v1: int, v2: int) -> dict:
        s1 = self.get_version(extension_id, v1)
        s2 = self.get_version(extension_id, v2)
        if not s1 or not s2:
            return {"error": "Version not found"}
        names1 = {f["name"] for f in s1.fields}
        names2 = {f["name"] for f in s2.fields}
        return {
            "added": sorted(names2 - names1),
            "removed": sorted(names1 - names2),
            "common": sorted(names1 & names2),
        }

    def list_versions(self, extension_id: str) -> list[dict]:
        return [{"version": s.version, "field_count": len(s.fields),
                 "schema_id": s.schema_id}
                for s in self._schemas.get(extension_id, [])]
