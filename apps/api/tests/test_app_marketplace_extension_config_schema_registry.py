from app.services.app_marketplace_extension_config_schema_registry import (
    ConfigSchemaRegistryService,
)
import pytest


FIELDS = [
    {"name": "theme", "type": "string", "required": True, "enum": ["light", "dark"]},
    {"name": "max_items", "type": "integer", "required": True, "default": 50},
    {"name": "debug", "type": "boolean"},
]


def test_register_and_get():
    svc = ConfigSchemaRegistryService()
    schema = svc.register("ext-1", FIELDS)
    assert schema.version == 1
    latest = svc.get_latest("ext-1")
    assert latest.schema_id == schema.schema_id


def test_versioning():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", [{"name": "a", "type": "string"}])
    svc.register("ext-1", [{"name": "a", "type": "string"}, {"name": "b", "type": "integer"}])
    assert svc.get_latest("ext-1").version == 2
    assert len(svc.list_versions("ext-1")) == 2


def test_validate_valid():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", FIELDS)
    result = svc.validate("ext-1", {"theme": "dark", "max_items": 100})
    assert result["valid"] is True


def test_validate_missing_required():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", FIELDS)
    result = svc.validate("ext-1", {"debug": True})
    assert result["valid"] is False
    assert any("theme" in e for e in result["errors"])


def test_default_applied():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", FIELDS)
    result = svc.validate("ext-1", {"theme": "light"})
    assert result["defaults_applied"]["max_items"] == 50


def test_type_mismatch():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", FIELDS)
    result = svc.validate("ext-1", {"theme": "dark", "max_items": "not_int"})
    assert result["valid"] is False
    assert any("expected integer" in e for e in result["errors"])


def test_enum_validation():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", FIELDS)
    result = svc.validate("ext-1", {"theme": "neon", "max_items": 10})
    assert result["valid"] is False
    assert any("must be one of" in e for e in result["errors"])


def test_diff_versions():
    svc = ConfigSchemaRegistryService()
    svc.register("ext-1", [{"name": "a", "type": "string"}, {"name": "b", "type": "integer"}])
    svc.register("ext-1", [{"name": "b", "type": "integer"}, {"name": "c", "type": "boolean"}])
    diff = svc.diff_versions("ext-1", 1, 2)
    assert diff["added"] == ["c"]
    assert diff["removed"] == ["a"]
    assert diff["common"] == ["b"]


def test_invalid_field_type():
    svc = ConfigSchemaRegistryService()
    with pytest.raises(ValueError, match="Invalid type"):
        svc.register("ext-1", [{"name": "x", "type": "uuid"}])
