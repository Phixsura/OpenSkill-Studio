"""Config Schema Registry — schema versioning with compatibility evolution.

Implements:
- Schema registration with version history
- Backward compatibility check (new schema can read old data)
- Forward compatibility check (old schema can read new data)
- Full compatibility (both directions)
- Breaking change detection
"""
from __future__ import annotations
from dataclasses import dataclass, field


class CompatLevel:
    NONE = "none"
    BACKWARD = "backward"       # new can read old
    FORWARD = "forward"         # old can read new
    FULL = "full"               # both directions


@dataclass
class SchemaVersion:
    version: int
    schema: dict  # simplified JSON schema
    registered_at: float = 0.0


@dataclass
class CompatResult:
    compatible: bool
    level: str
    issues: list[str] = field(default_factory=list)


class ConfigSchemaRegService:
    def __init__(self):
        self._schemas: dict[str, list[SchemaVersion]] = {}  # subject -> versions
        self._compat_level: dict[str, str] = {}  # subject -> required compat level

    def register(self, subject: str, schema: dict) -> tuple[bool, SchemaVersion | str]:
        """Register a new schema version. Checks compatibility if configured."""
        if subject not in self._schemas:
            self._schemas[subject] = []

        version = len(self._schemas[subject]) + 1
        
        # Check compatibility with previous version
        if self._schemas[subject]:
            required = self._compat_level.get(subject, CompatLevel.BACKWARD)
            if required != CompatLevel.NONE:
                prev = self._schemas[subject][-1]
                result = self.check_compat(prev.schema, schema, required)
                if not result.compatible:
                    return False, f"Incompatible: {'; '.join(result.issues)}"

        import time
        sv = SchemaVersion(version=version, schema=schema, registered_at=time.time())
        self._schemas[subject].append(sv)
        return True, sv

    def set_compat_level(self, subject: str, level: str) -> None:
        self._compat_level[subject] = level

    def check_compat(self, old_schema: dict, new_schema: dict,
                     level: str) -> CompatResult:
        """Check if new schema is compatible with old at given level."""
        issues = []
        old_props = old_schema.get("properties", {})
        new_props = new_schema.get("properties", {})
        old_required = set(old_schema.get("required", []))
        new_required = set(new_schema.get("required", []))

        if level in (CompatLevel.BACKWARD, CompatLevel.FULL):
            # BACKWARD: new schema must be able to read old data
            # - Can't remove fields that old data has (unless optional)
            # - Can't change types of existing fields
            # - New required fields break backward compat (old data won't have them)
            for name in old_props:
                if name not in new_props:
                    issues.append(f"Removed field '{name}' breaks backward compat")
                else:
                    old_type = old_props[name].get("type")
                    new_type = new_props[name].get("type")
                    if old_type and new_type and old_type != new_type:
                        issues.append(f"Type change '{name}': {old_type}→{new_type}")

            new_only_required = new_required - old_required
            for name in new_only_required:
                if name not in old_props:
                    issues.append(f"New required field '{name}' breaks backward compat")

        if level in (CompatLevel.FORWARD, CompatLevel.FULL):
            # FORWARD: old schema must be able to read new data
            # - Can't add required fields (old schema won't expect them)
            # - Can't narrow types
            for name in new_props:
                if name not in old_props and name in new_required:
                    issues.append(f"New required field '{name}' breaks forward compat")

            # Removed required fields break forward compat
            for name in old_required:
                if name not in new_required and name in new_props:
                    issues.append(f"Required→optional '{name}' breaks forward compat")

        return CompatResult(
            compatible=len(issues) == 0,
            level=level,
            issues=issues)

    def get_latest(self, subject: str) -> SchemaVersion | None:
        versions = self._schemas.get(subject, [])
        return versions[-1] if versions else None

    def get_version(self, subject: str, version: int) -> SchemaVersion | None:
        versions = self._schemas.get(subject, [])
        if 1 <= version <= len(versions):
            return versions[version - 1]
        return None

    def get_all_versions(self, subject: str) -> list[SchemaVersion]:
        return list(self._schemas.get(subject, []))
