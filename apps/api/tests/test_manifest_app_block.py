"""Manifest app block validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

def test_app_block_missing():
    r = validate_manifest({"schema_version": "1.0"})
    assert any("app" in e for e in r.errors)

def test_app_block_not_dict():
    r = validate_manifest({"schema_version": "1.0", "app": "string"})
    assert any("app" in e for e in r.errors)

def test_app_block_empty():
    r = validate_manifest({"schema_version": "1.0", "app": {}})
    assert any("name" in e for e in r.errors)

def test_app_with_all_fields():
    r = validate_manifest({"schema_version": "1.0", "app": {
        "name": "My App", "slug": "my-app", "version": "1.0.0",
        "category": "connector", "min_platform_version": "1.0.0",
    }})
    app_errors = [e for e in r.errors if "app." in e]
    assert app_errors == []

def test_app_invalid_category():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "category": "invalid"}})
    assert any("category" in e for e in r.errors)

def test_app_invalid_slug():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "slug": "BAD SLUG!"}})
    assert any("slug" in e for e in r.errors)

def test_app_invalid_version():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "version": "not-semver"}})
    assert any("version" in e or "semver" in e.lower() for e in r.errors)

def test_app_name_too_long():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "X" * 101}})
    assert any("100" in e for e in r.errors)
