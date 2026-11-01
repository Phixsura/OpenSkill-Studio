"""Tests for Event Schema Registry — versioning, validation, compatibility, deprecation."""

from datetime import UTC, datetime, timedelta

import pytest

from app.services.event_schema_registry import (
    CompatibilityResult,
    EventSchemaRegistry,
    SchemaStatus,
)

SKILL_PACK_SCHEMA = {
    "type": "object",
    "required": ["pack_id", "name", "version"],
    "properties": {
        "pack_id": {"type": "string"},
        "name": {"type": "string"},
        "version": {"type": "string"},
        "author": {"type": "string"},
        "tags": {"type": "array"},
    },
}


class TestRegistration:
    def test_register_new_event(self):
        reg = EventSchemaRegistry()
        entry = reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "Skill pack was published")
        assert entry.event_type == "skill_pack.published"
        assert entry.version == 1
        assert entry.status == SchemaStatus.ACTIVE

    def test_auto_increment_version(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        e2 = reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v2")
        assert e2.version == 2
        assert reg.get_latest_version("skill_pack.published") == 2

    def test_invalid_event_type_rejected(self):
        reg = EventSchemaRegistry()
        with pytest.raises(ValueError, match="Invalid event_type"):
            reg.register("InvalidType", SKILL_PACK_SCHEMA, "bad")

    def test_invalid_event_type_no_dot(self):
        reg = EventSchemaRegistry()
        with pytest.raises(ValueError, match="Invalid event_type"):
            reg.register("nodot", SKILL_PACK_SCHEMA, "bad")

    def test_invalid_schema_rejected(self):
        reg = EventSchemaRegistry()
        with pytest.raises(ValueError, match="JSON Schema"):
            reg.register("skill_pack.published", {"no_type": True}, "bad")

    def test_example_payload_stored(self):
        reg = EventSchemaRegistry()
        example = {"pack_id": "01ABC", "name": "React", "version": "1.0.0"}
        entry = reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "desc", example)
        assert entry.example_payload == example


class TestQuerying:
    def test_get_latest(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v2")
        entry = reg.get("skill_pack.published")
        assert entry is not None
        assert entry.version == 2

    def test_get_specific_version(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v2")
        entry = reg.get("skill_pack.published", version=1)
        assert entry is not None
        assert entry.version == 1

    def test_get_nonexistent_returns_none(self):
        reg = EventSchemaRegistry()
        assert reg.get("nonexistent.event") is None

    def test_list_event_types(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "a")
        reg.register("app.installed", SKILL_PACK_SCHEMA, "b")
        reg.register("workflow.completed", SKILL_PACK_SCHEMA, "c")
        types = reg.list_event_types()
        names = [t.event_type for t in types]
        assert names == ["app.installed", "skill_pack.published", "workflow.completed"]

    def test_list_event_types_filter_status(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "active")
        reg.register("old.event", SKILL_PACK_SCHEMA, "deprecated")
        reg.deprecate("old.event")
        active = reg.list_event_types(status=SchemaStatus.ACTIVE)
        assert len(active) == 1
        assert active[0].event_type == "skill_pack.published"

    def test_list_versions(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v2")
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v3")
        versions = reg.list_versions("skill_pack.published")
        assert [v.version for v in versions] == [1, 2, 3]


class TestDeprecation:
    def test_deprecate_marks_status(self):
        reg = EventSchemaRegistry()
        reg.register("old.event", SKILL_PACK_SCHEMA, "old")
        entry = reg.deprecate("old.event", message="Use new.event instead")
        assert entry.status == SchemaStatus.DEPRECATED
        assert entry.deprecated_at is not None
        assert entry.deprecation_message == "Use new.event instead"

    def test_deprecate_with_sunset(self):
        reg = EventSchemaRegistry()
        reg.register("old.event", SKILL_PACK_SCHEMA, "old")
        sunset = datetime.now(UTC) + timedelta(days=90)
        entry = reg.deprecate("old.event", sunset_at=sunset)
        assert entry.sunset_at == sunset

    def test_deprecate_nonexistent_raises(self):
        reg = EventSchemaRegistry()
        with pytest.raises(ValueError, match="not found"):
            reg.deprecate("nonexistent.event")

    def test_retire_blocks_validation(self):
        reg = EventSchemaRegistry()
        reg.register("old.event", SKILL_PACK_SCHEMA, "old")
        reg.retire("old.event", version=1)
        result = reg.validate("old.event", {"pack_id": "x", "name": "y", "version": "1"}, version=1)
        assert result.valid is False
        assert "retired" in result.errors[0].lower()


class TestValidation:
    def test_valid_payload(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        result = reg.validate("skill_pack.published", {
            "pack_id": "01ABC", "name": "React Patterns", "version": "2.0.0",
        })
        assert result.valid is True
        assert result.errors == []

    def test_missing_required_field(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        result = reg.validate("skill_pack.published", {"pack_id": "01ABC"})
        assert result.valid is False
        assert any("name" in e for e in result.errors)
        assert any("version" in e for e in result.errors)

    def test_wrong_type(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        result = reg.validate("skill_pack.published", {
            "pack_id": 123, "name": "Test", "version": "1.0",
        })
        assert result.valid is False
        assert any("pack_id" in e for e in result.errors)

    def test_extra_fields_allowed(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        result = reg.validate("skill_pack.published", {
            "pack_id": "01ABC", "name": "Test", "version": "1.0", "extra": "ok",
        })
        assert result.valid is True

    def test_unknown_event_type(self):
        reg = EventSchemaRegistry()
        result = reg.validate("unknown.event", {"data": "test"})
        assert result.valid is False
        assert "No schema found" in result.errors[0]

    def test_boolean_not_integer(self):
        reg = EventSchemaRegistry()
        schema = {"type": "object", "required": ["count"], "properties": {"count": {"type": "integer"}}}
        reg.register("test.event", schema, "test")
        result = reg.validate("test.event", {"count": True})
        assert result.valid is False


class TestCompatibility:
    def test_first_version_always_compatible(self):
        reg = EventSchemaRegistry()
        report = reg.check_compatibility("new.event", SKILL_PACK_SCHEMA)
        assert report.result == CompatibilityResult.COMPATIBLE

    def test_adding_optional_field_compatible(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        new_schema = {
            **SKILL_PACK_SCHEMA,
            "properties": {
                **SKILL_PACK_SCHEMA["properties"],
                "downloads": {"type": "integer"},
            },
        }
        report = reg.check_compatibility("skill_pack.published", new_schema)
        assert report.result == CompatibilityResult.COMPATIBLE
        assert any("downloads" in a for a in report.additions)

    def test_adding_required_field_breaking(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        new_schema = {
            **SKILL_PACK_SCHEMA,
            "required": [*SKILL_PACK_SCHEMA["required"], "category"],
            "properties": {
                **SKILL_PACK_SCHEMA["properties"],
                "category": {"type": "string"},
            },
        }
        report = reg.check_compatibility("skill_pack.published", new_schema)
        assert report.result == CompatibilityResult.BREAKING
        assert any("category" in b for b in report.breaking_changes)

    def test_removing_property_breaking(self):
        reg = EventSchemaRegistry()
        reg.register("skill_pack.published", SKILL_PACK_SCHEMA, "v1")
        reduced = {
            "type": "object",
            "required": ["pack_id", "name"],
            "properties": {
                "pack_id": {"type": "string"},
                "name": {"type": "string"},
                # version and others removed
            },
        }
        report = reg.check_compatibility("skill_pack.published", reduced)
        assert report.result == CompatibilityResult.BREAKING
        assert any("Removed" in b for b in report.breaking_changes)
