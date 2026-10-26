from app.services.app_marketplace_extension_config_validator import (
    ConfigValidator, FieldValidator,
)

SCHEMA = [
    FieldValidator("name", "string", required=True, min_length=1, max_length=100),
    FieldValidator("port", "int", required=True, min_val=1024, max_val=65535),
    FieldValidator("url", "url", required=True),
    FieldValidator("email", "email", required=False),
    FieldValidator("mode", "enum", required=True, enum_values=["dev", "prod", "test"]),
    FieldValidator("debug", "bool", required=False, default=False),
    FieldValidator("timeout", "float", required=False, default=30.0, min_val=1, max_val=300),
]


def test_valid_config():
    cv = ConfigValidator()
    cv.register_schema("ext-1", SCHEMA)
    ok, errors, processed = cv.validate("ext-1", {
        "name": "My Extension", "port": 3000, "url": "https://api.test.com",
        "mode": "prod",
    })
    assert ok is True
    assert processed["debug"] is False  # default applied


def test_missing_required():
    cv = ConfigValidator()
    cv.register_schema("ext-2", SCHEMA)
    ok, errors, _ = cv.validate("ext-2", {"name": "Test"})
    assert ok is False
    assert any("port" in e for e in errors)


def test_type_error():
    cv = ConfigValidator()
    cv.register_schema("ext-3", SCHEMA)
    ok, errors, _ = cv.validate("ext-3", {"name": "Test", "port": "not_int", "url": "https://a.com", "mode": "dev"})
    assert ok is False
    assert any("expected int" in e for e in errors)


def test_range_error():
    cv = ConfigValidator()
    cv.register_schema("ext-4", SCHEMA)
    ok, errors, _ = cv.validate("ext-4", {"name": "Test", "port": 80, "url": "https://a.com", "mode": "dev"})
    assert ok is False
    assert any("below minimum" in e for e in errors)


def test_url_validation():
    cv = ConfigValidator()
    cv.register_schema("ext-5", SCHEMA)
    ok, errors, _ = cv.validate("ext-5", {"name": "T", "port": 3000, "url": "not-a-url", "mode": "dev"})
    assert ok is False
    assert any("URL" in e for e in errors)


def test_enum_validation():
    cv = ConfigValidator()
    cv.register_schema("ext-6", SCHEMA)
    ok, errors, _ = cv.validate("ext-6", {"name": "T", "port": 3000, "url": "https://a.com", "mode": "invalid"})
    assert ok is False
    assert any("must be one of" in e for e in errors)


def test_email_validation():
    cv = ConfigValidator()
    cv.register_schema("ext-7", SCHEMA)
    ok, errors, _ = cv.validate("ext-7", {
        "name": "T", "port": 3000, "url": "https://a.com", "mode": "dev", "email": "bad",
    })
    assert ok is False
    assert any("email" in e for e in errors)
