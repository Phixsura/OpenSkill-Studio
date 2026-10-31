from app.services.app_marketplace_extension_config_schema_reg import (
    ConfigSchemaRegService, CompatLevel
)


def test_register_first_schema():
    svc = ConfigSchemaRegService()
    ok, sv = svc.register("user-config", {
        "properties": {"name": {"type": "string"}, "age": {"type": "integer"}},
        "required": ["name"]
    })
    assert ok is True
    assert sv.version == 1


def test_backward_compat_add_optional():
    svc = ConfigSchemaRegService()
    svc.register("cfg", {"properties": {"a": {"type": "string"}}, "required": ["a"]})
    # Adding optional field is backward compatible
    ok, sv = svc.register("cfg", {
        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
        "required": ["a"]
    })
    assert ok is True
    assert sv.version == 2


def test_backward_compat_remove_field_breaks():
    svc = ConfigSchemaRegService()
    svc.register("cfg", {
        "properties": {"a": {"type": "string"}, "b": {"type": "integer"}},
        "required": ["a"]
    })
    ok, msg = svc.register("cfg", {
        "properties": {"a": {"type": "string"}},
        "required": ["a"]
    })
    assert ok is False
    assert "Removed field" in msg


def test_backward_compat_type_change_breaks():
    svc = ConfigSchemaRegService()
    svc.register("cfg", {"properties": {"count": {"type": "integer"}}})
    ok, msg = svc.register("cfg", {"properties": {"count": {"type": "string"}}})
    assert ok is False
    assert "Type change" in msg


def test_backward_compat_new_required_breaks():
    svc = ConfigSchemaRegService()
    svc.register("cfg", {"properties": {"a": {"type": "string"}}})
    ok, msg = svc.register("cfg", {
        "properties": {"a": {"type": "string"}, "b": {"type": "string"}},
        "required": ["b"]
    })
    assert ok is False
    assert "required" in msg.lower()


def test_none_compat_allows_anything():
    svc = ConfigSchemaRegService()
    svc.set_compat_level("cfg", CompatLevel.NONE)
    svc.register("cfg", {"properties": {"a": {"type": "string"}}})
    ok, _ = svc.register("cfg", {"properties": {"completely": {"type": "integer"}}})
    assert ok is True


def test_full_compat():
    svc = ConfigSchemaRegService()
    svc.set_compat_level("cfg", CompatLevel.FULL)
    svc.register("cfg", {
        "properties": {"a": {"type": "string"}},
        "required": ["a"]
    })
    # Adding required field breaks both directions
    result = svc.check_compat(
        {"properties": {"a": {"type": "string"}}, "required": ["a"]},
        {"properties": {"a": {"type": "string"}, "b": {"type": "string"}}, "required": ["a", "b"]},
        CompatLevel.FULL
    )
    assert result.compatible is False


def test_version_history():
    svc = ConfigSchemaRegService()
    svc.register("cfg", {"properties": {"v1": {"type": "string"}}})
    svc.set_compat_level("cfg", CompatLevel.NONE)
    svc.register("cfg", {"properties": {"v2": {"type": "string"}}})
    assert len(svc.get_all_versions("cfg")) == 2
    assert svc.get_version("cfg", 1).schema["properties"].get("v1") is not None
    assert svc.get_latest("cfg").version == 2
