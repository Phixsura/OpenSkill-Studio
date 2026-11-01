"""Manifest slug validation — comprehensive."""

import pytest
from app.services.manifest_validator import validate_manifest

BASE = {"schema_version": "1.0", "permissions": ["read:cohorts"]}

VALID_SLUGS = ["my-app", "test-connector", "ab", "a-b-c-d", "app123", "my-app-v2"]

@pytest.mark.parametrize("slug", VALID_SLUGS)
def test_valid_slug(slug):
    m = {**BASE, "app": {"name": "App", "slug": slug, "version": "1.0.0", "category": "connector"}}
    r = validate_manifest(m)
    slug_errors = [e for e in r.errors if "slug" in e.lower()]
    assert slug_errors == [], f"{slug}: {slug_errors}"

INVALID_SLUGS = [
    "A",                    # too short + uppercase
    "My App",               # spaces
    "my_app",               # underscores
    "MY-APP",               # uppercase
    "a" * 100,              # too long
]

@pytest.mark.parametrize("slug", INVALID_SLUGS)
def test_invalid_slug(slug):
    m = {**BASE, "app": {"name": "App", "slug": slug, "version": "1.0.0", "category": "connector"}}
    r = validate_manifest(m)
    assert not r.valid or any("slug" in e.lower() for e in r.errors)
