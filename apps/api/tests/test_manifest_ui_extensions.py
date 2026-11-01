"""Manifest UI extension validation."""

import pytest
from app.services.manifest_validator import validate_manifest, VALID_SURFACES

BASE = {
    "schema_version": "1.0",
    "app": {"name": "UI App", "slug": "ui-app", "version": "1.0.0", "category": "ui_extension"},
    "permissions": ["extend:ui"],
}

@pytest.mark.parametrize("surface", sorted(VALID_SURFACES))
def test_each_surface_in_extension(surface):
    m = {**BASE, "ui_extensions": [{"surface": surface, "title": "Test", "entry": "test.html"}]}
    r = validate_manifest(m)
    surface_errors = [e for e in r.errors if "surface" in e.lower()]
    assert surface_errors == [], f"{surface}: {surface_errors}"

def test_multiple_extensions():
    m = {**BASE, "ui_extensions": [
        {"surface": "dashboard_card", "title": "Card 1", "entry": "c1.html"},
        {"surface": "project_sidebar", "title": "Sidebar", "entry": "s.html"},
    ]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_extension_with_viewport():
    m = {**BASE, "ui_extensions": [
        {"surface": "dashboard_card", "title": "Card", "entry": "c.html",
         "viewport": {"width": 400, "height": 300}},
    ]}
    r = validate_manifest(m)
    assert r.valid, f"Errors: {r.errors}"

def test_extension_missing_title():
    m = {**BASE, "ui_extensions": [
        {"surface": "dashboard_card", "entry": "c.html"},
    ]}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0

def test_extension_missing_entry():
    m = {**BASE, "ui_extensions": [
        {"surface": "dashboard_card", "title": "Card"},
    ]}
    r = validate_manifest(m)
    assert not r.valid or len(r.errors) > 0
