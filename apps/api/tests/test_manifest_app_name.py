"""App name validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

@pytest.mark.parametrize("name", ["AB", "Test App", "My Connector v2", "A" * 100])
def test_valid_names(name):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": name}})
    name_errors = [e for e in r.errors if "name" in e]
    assert name_errors == []

@pytest.mark.parametrize("name", ["", None])
def test_invalid_names(name):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": name} if name is not None else {"slug": "x"}})
    assert any("name" in e for e in r.errors)

def test_name_too_long():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "A" * 101}})
    assert any("100" in e for e in r.errors)
