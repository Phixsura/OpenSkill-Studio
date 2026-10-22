"""CreateAppVersionRequest schema tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateAppVersionRequest

def test_valid_version():
    r = CreateAppVersionRequest(
        version="1.0.0",
        manifest={"schema_version": "1.0", "app": {"name": "X", "slug": "x", "version": "1.0.0", "category": "connector"}, "permissions": ["read:cohorts"]},
        release_notes="Initial release",
    )
    assert r.version == "1.0.0"

def test_missing_version():
    with pytest.raises(ValidationError):
        CreateAppVersionRequest(
            manifest={"schema_version": "1.0"},
            release_notes="test",
        )

def test_missing_manifest():
    with pytest.raises(ValidationError):
        CreateAppVersionRequest(
            version="1.0.0",
            release_notes="test",
        )

def test_optional_release_notes():
    r = CreateAppVersionRequest(
        version="1.0.0",
        manifest={"schema_version": "1.0", "app": {"name": "X", "slug": "x", "version": "1.0.0", "category": "connector"}},
    )
    assert r.version == "1.0.0"

VERSIONS = ["0.0.1", "1.0.0", "2.3.4-beta", "10.0.0"]

@pytest.mark.parametrize("ver", VERSIONS)
def test_various_versions(ver):
    r = CreateAppVersionRequest(
        version=ver,
        manifest={"schema_version": "1.0", "app": {"name": "X", "slug": "x", "version": ver, "category": "connector"}},
    )
    assert r.version == ver
