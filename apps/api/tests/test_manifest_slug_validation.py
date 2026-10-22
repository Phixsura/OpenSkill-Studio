"""Manifest slug validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_SLUGS = ["ab", "my-app", "test-connector-v2", "a" * 60]
INVALID_SLUGS = ["A", "My App", "has space", "UPPER", "a"]  # 'a' is 1 char, regex needs 2+

@pytest.mark.parametrize("slug", VALID_SLUGS)
def test_valid_slug(slug):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "slug": slug}})
    slug_errors = [e for e in r.errors if "slug" in e]
    assert slug_errors == [], f"Slug '{slug}' rejected"

@pytest.mark.parametrize("slug", INVALID_SLUGS)
def test_invalid_slug(slug):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T", "slug": slug}})
    slug_errors = [e for e in r.errors if "slug" in e]
    assert len(slug_errors) >= 1, f"Slug '{slug}' accepted"
