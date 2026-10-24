"""Manifest validator result object tests."""

import pytest
from app.services.manifest_validator import validate_manifest

def test_result_has_valid():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "X", "slug": "xx", "version": "1.0.0", "category": "connector"}, "permissions": []})
    assert hasattr(r, "valid")
    assert isinstance(r.valid, bool)

def test_result_has_errors():
    r = validate_manifest({})
    assert hasattr(r, "errors")
    assert isinstance(r.errors, list)

def test_result_has_warnings():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "X", "slug": "xx", "version": "1.0.0", "category": "connector"}, "permissions": []})
    assert hasattr(r, "warnings")
    assert isinstance(r.warnings, list)

def test_valid_manifest_no_errors():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "X", "slug": "xx", "version": "1.0.0", "category": "connector"}, "permissions": ["read:cohorts"]})
    assert r.valid is True
    assert r.errors == []

def test_invalid_manifest_has_errors():
    r = validate_manifest({})
    assert r.valid is False
    assert len(r.errors) > 0

def test_errors_are_strings():
    r = validate_manifest({})
    for err in r.errors:
        assert isinstance(err, str)
