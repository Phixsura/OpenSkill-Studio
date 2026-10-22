"""CreateAppVersionRequest schema tests."""

import pytest
from pydantic import ValidationError
from app.schemas.developer import CreateAppVersionRequest

MANIFEST = {"schema_version": "1.0", "app": {"name": "X", "slug": "x", "version": "1.0.0", "category": "connector"}, "permissions": ["read:cohorts"]}

def test_valid_version():
    r = CreateAppVersionRequest(version="1.0.0", manifest=MANIFEST, content_hash="abc123")
    assert r.version == "1.0.0"

def test_with_changelog():
    r = CreateAppVersionRequest(version="1.0.0", manifest=MANIFEST, content_hash="abc", changelog="Initial")
    assert r.changelog == "Initial"

def test_missing_version():
    with pytest.raises(ValidationError):
        CreateAppVersionRequest(manifest=MANIFEST, content_hash="abc")

def test_missing_manifest():
    with pytest.raises(ValidationError):
        CreateAppVersionRequest(version="1.0.0", content_hash="abc")

def test_missing_content_hash():
    with pytest.raises(ValidationError):
        CreateAppVersionRequest(version="1.0.0", manifest=MANIFEST)

VERSIONS = ["0.0.1", "1.0.0", "2.3.4"]

@pytest.mark.parametrize("ver", VERSIONS)
def test_various_versions(ver):
    r = CreateAppVersionRequest(version=ver, manifest=MANIFEST, content_hash="hash123")
    assert r.version == ver
