"""App config validator tests."""

import pytest
from app.services.app_config_validator import validate_config

SCHEMA = {
    "type": "object",
    "properties": {
        "api_url": {"type": "string", "minLength": 5},
        "timeout": {"type": "integer"},
        "enabled": {"type": "boolean"},
        "mode": {"type": "string", "enum": ["fast", "slow", "auto"]},
    },
    "required": ["api_url"],
}

def test_valid_config():
    errors = validate_config({"api_url": "https://api.example.com", "timeout": 30}, SCHEMA)
    assert errors == []

def test_missing_required():
    errors = validate_config({"timeout": 30}, SCHEMA)
    assert any("api_url" in e for e in errors)

def test_wrong_type_string():
    errors = validate_config({"api_url": 123}, SCHEMA)
    assert any("string" in e for e in errors)

def test_wrong_type_integer():
    errors = validate_config({"api_url": "https://x.com", "timeout": "not-int"}, SCHEMA)
    assert any("integer" in e for e in errors)

def test_wrong_type_boolean():
    errors = validate_config({"api_url": "https://x.com", "enabled": "yes"}, SCHEMA)
    assert any("boolean" in e for e in errors)

def test_min_length():
    errors = validate_config({"api_url": "ab"}, SCHEMA)
    assert any("at least" in e for e in errors)

def test_enum_valid():
    errors = validate_config({"api_url": "https://x.com", "mode": "fast"}, SCHEMA)
    assert errors == []

def test_enum_invalid():
    errors = validate_config({"api_url": "https://x.com", "mode": "turbo"}, SCHEMA)
    assert any("one of" in e for e in errors)

def test_additional_properties_false():
    schema = {**SCHEMA, "additionalProperties": False}
    errors = validate_config({"api_url": "https://x.com", "unknown_field": "x"}, schema)
    assert any("Unknown" in e for e in errors)

def test_additional_properties_allowed():
    errors = validate_config({"api_url": "https://x.com", "extra": "ok"}, SCHEMA)
    assert errors == []

def test_empty_config_missing_required():
    errors = validate_config({}, SCHEMA)
    assert len(errors) > 0

def test_no_schema():
    errors = validate_config({"anything": "goes"}, {})
    assert errors == []

def test_non_dict_config():
    errors = validate_config("not-a-dict", SCHEMA)
    assert any("object" in e for e in errors)
