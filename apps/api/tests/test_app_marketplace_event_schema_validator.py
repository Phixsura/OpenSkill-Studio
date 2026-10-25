from app.services.app_marketplace_event_schema_validator import (
    EventSchemaValidator, EventSchema, FieldSchema,
)


def _setup() -> EventSchemaValidator:
    v = EventSchemaValidator()
    v.register(EventSchema("extension.installed", 1, [
        FieldSchema("extension_id", "string", required=True, min_length=1),
        FieldSchema("org_id", "string", required=True),
        FieldSchema("version", "string"),
        FieldSchema("source", "enum", required=False, enum_values=["marketplace", "api", "cli"]),
    ], "Fired when an extension is installed"))
    return v


def test_valid_payload():
    v = _setup()
    ok, errors = v.validate("extension.installed", {
        "extension_id": "ext-1", "org_id": "org-1", "version": "2.0.0",
    })
    assert ok is True


def test_missing_required():
    v = _setup()
    ok, errors = v.validate("extension.installed", {"extension_id": "ext-1"})
    assert ok is False
    assert any("org_id" in e for e in errors)


def test_wrong_type():
    v = _setup()
    ok, errors = v.validate("extension.installed", {
        "extension_id": 123, "org_id": "org-1",
    })
    assert ok is False
    assert any("expected string" in e for e in errors)


def test_enum_validation():
    v = _setup()
    ok, errors = v.validate("extension.installed", {
        "extension_id": "ext-1", "org_id": "org-1", "source": "invalid_source",
    })
    assert ok is False
    assert any("must be one of" in e for e in errors)


def test_valid_enum():
    v = _setup()
    ok, _ = v.validate("extension.installed", {
        "extension_id": "ext-1", "org_id": "org-1", "source": "marketplace",
    })
    assert ok is True


def test_min_length():
    v = _setup()
    ok, errors = v.validate("extension.installed", {
        "extension_id": "", "org_id": "org-1",
    })
    assert ok is False  # empty string fails required


def test_unknown_fields_soft():
    v = _setup()
    ok, errors = v.validate("extension.installed", {
        "extension_id": "ext-1", "org_id": "org-1", "extra_field": "val",
    })
    assert ok is True  # unknown fields are warnings, not errors
    assert any("Unknown" in e for e in errors)


def test_no_schema_passes():
    v = EventSchemaValidator()
    ok, errors = v.validate("unregistered.event", {"anything": "goes"})
    assert ok is True
