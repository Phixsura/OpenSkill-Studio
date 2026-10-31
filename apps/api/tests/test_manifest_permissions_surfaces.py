"""Manifest validator — individual permission and surface coverage."""

import pytest
from app.services.manifest_validator import validate_manifest, VALID_PERMISSIONS, VALID_SURFACES, VALID_CATEGORIES

BASE = {
    "schema_version": "1.0",
    "app": {"name": "X", "slug": "test-app", "version": "1.0.0", "category": "connector"},
}

@pytest.mark.parametrize("perm", sorted(VALID_PERMISSIONS))
def test_each_permission_accepted(perm):
    m = {**BASE, "permissions": [perm]}
    r = validate_manifest(m)
    perm_errors = [e for e in r.errors if "permission" in e.lower()]
    assert perm_errors == [], f"{perm} rejected: {perm_errors}"

@pytest.mark.parametrize("surface", sorted(VALID_SURFACES))
def test_each_surface_accepted(surface):
    m = {**BASE, "permissions": ["extend:ui"],
         "ui_extensions": [{"surface": surface, "title": "Test", "entry": "test.html"}]}
    r = validate_manifest(m)
    surface_errors = [e for e in r.errors if "surface" in e.lower()]
    assert surface_errors == [], f"{surface} rejected: {surface_errors}"

@pytest.mark.parametrize("cat", sorted(VALID_CATEGORIES))
def test_each_category_accepted(cat):
    m = {"schema_version": "1.0",
         "app": {"name": "X", "slug": "test-app", "version": "1.0.0", "category": cat},
         "permissions": ["read:cohorts"]}
    r = validate_manifest(m)
    cat_errors = [e for e in r.errors if "category" in e.lower()]
    assert cat_errors == [], f"{cat} rejected: {cat_errors}"

INVALID_PERMISSIONS = ["admin:everything", "delete:users", "read:", ":cohorts", ""]

@pytest.mark.parametrize("perm", INVALID_PERMISSIONS)
def test_invalid_permission_rejected(perm):
    m = {**BASE, "permissions": [perm]}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0 or len(r.warnings) > 0
