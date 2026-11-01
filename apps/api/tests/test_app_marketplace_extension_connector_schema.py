from app.services.app_marketplace_extension_connector_schema import (
    ConnectorSchemaService,
)


def test_valid_input():
    svc = ConnectorSchemaService()
    svc.register_schema("slack", "1.0", [
        {"name": "channel", "type": "string", "required": True},
        {"name": "message", "type": "string", "required": True, "min_length": 1},
    ])
    result = svc.validate("slack", {"channel": "#general", "message": "Hello"})
    assert result.valid is True


def test_missing_required():
    svc = ConnectorSchemaService()
    svc.register_schema("slack", "1.0", [
        {"name": "channel", "type": "string"},
        {"name": "token", "type": "string"},
    ])
    result = svc.validate("slack", {"channel": "#general"})
    assert result.valid is False
    assert any("token" in e for e in result.errors)


def test_wrong_type():
    svc = ConnectorSchemaService()
    svc.register_schema("api", "1.0", [
        {"name": "count", "type": "integer"},
    ])
    result = svc.validate("api", {"count": "five"})
    assert result.valid is False
    assert any("expected integer" in e for e in result.errors)


def test_default_value():
    svc = ConnectorSchemaService()
    svc.register_schema("api", "1.0", [
        {"name": "timeout", "type": "integer", "required": True, "default": 30},
    ])
    result = svc.validate("api", {})
    assert result.valid is True
    assert result.coerced_values["timeout"] == 30


def test_enum_validation():
    svc = ConnectorSchemaService()
    svc.register_schema("api", "1.0", [
        {"name": "method", "type": "string", "enum": ["GET", "POST", "PUT"]},
    ])
    result = svc.validate("api", {"method": "DELETE"})
    assert result.valid is False
    assert any("must be one of" in e for e in result.errors)


def test_email_validation():
    svc = ConnectorSchemaService()
    svc.register_schema("mail", "1.0", [{"name": "to", "type": "email"}])
    r1 = svc.validate("mail", {"to": "user@example.com"})
    assert r1.valid is True
    r2 = svc.validate("mail", {"to": "not-an-email"})
    assert r2.valid is False


def test_unknown_fields_warned():
    svc = ConnectorSchemaService()
    svc.register_schema("api", "1.0", [{"name": "url", "type": "url"}])
    result = svc.validate("api", {"url": "https://example.com", "extra": "data"})
    assert result.valid is True
    assert any("Unknown field" in w for w in result.warnings)
