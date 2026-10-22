"""Schema version validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_VERSIONS = ["1.0", "1.1"]
WARN_VERSIONS = ["2.0", "3.0", "0.1"]

@pytest.mark.parametrize("sv", VALID_VERSIONS)
def test_valid_schema_version(sv):
    r = validate_manifest({"schema_version": sv, "app": {"name": "T"}})
    sv_warns = [w for w in r.warnings if "schema_version" in w]
    assert sv_warns == []

@pytest.mark.parametrize("sv", WARN_VERSIONS)
def test_warn_schema_version(sv):
    r = validate_manifest({"schema_version": sv, "app": {"name": "T"}})
    assert any(sv in w for w in r.warnings)

def test_missing_schema_version():
    r = validate_manifest({"app": {"name": "T"}})
    assert any("schema_version" in e for e in r.errors)
