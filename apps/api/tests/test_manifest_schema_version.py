"""Manifest schema_version validation."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_APP = {"name": "App", "slug": "sv-app", "version": "1.0.0", "category": "connector"}

def test_schema_version_1_0():
    r = validate_manifest({"schema_version": "1.0", "app": VALID_APP, "permissions": ["read:cohorts"]})
    sv_errors = [e for e in r.errors if "schema" in e.lower() and "version" in e.lower()]
    assert sv_errors == []

def test_missing_schema_version():
    r = validate_manifest({"app": VALID_APP, "permissions": ["read:cohorts"]})
    assert not r.valid

def test_invalid_schema_version():
    r = validate_manifest({"schema_version": "999.0", "app": VALID_APP, "permissions": []})
    assert not r.valid or len(r.warnings) > 0

def test_schema_version_empty():
    r = validate_manifest({"schema_version": "", "app": VALID_APP, "permissions": []})
    assert not r.valid
