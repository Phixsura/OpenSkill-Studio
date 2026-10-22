"""Tests for manifest secret declaration validation."""

from app.services.manifest_validator import validate_manifest

def test_secret_valid():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "secrets": [{"key": "API_KEY", "description": "key", "required": True}]})
    secret_errors = [e for e in r.errors if "secret" in e.lower()]
    assert secret_errors == []

def test_secret_missing_key():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "secrets": [{"description": "no key"}]})
    assert any("key" in e for e in r.errors)

def test_secret_invalid_key_format():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "secrets": [{"key": "lower-case!"}]})
    assert any("uppercase" in e for e in r.errors)

def test_secret_duplicate_keys():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "secrets": [{"key": "SAME"}, {"key": "SAME"}]})
    assert any("Duplicate" in e for e in r.errors)

def test_secret_non_dict():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "secrets": ["string"]})
    assert any("object" in e for e in r.errors)

def test_secret_multiple_valid():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"},
        "secrets": [{"key": "KEY_A"}, {"key": "KEY_B"}, {"key": "KEY_C"}]})
    secret_errors = [e for e in r.errors if "secret" in e.lower() or "key" in e.lower()]
    assert secret_errors == []

def test_no_secrets():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}})
    assert r.valid

def test_empty_secrets_list():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "secrets": []})
    assert r.valid
