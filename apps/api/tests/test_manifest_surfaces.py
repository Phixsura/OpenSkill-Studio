"""Tests for UI surface validation in manifests."""

from app.services.manifest_validator import VALID_SURFACES, validate_manifest


def test_every_surface_accepted():
    for surface in VALID_SURFACES:
        r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
            "ui_extensions": [{"surface": surface, "title": "T", "entry": "t.html"}]})
        surface_errors = [e for e in r.errors if surface in e]
        assert surface_errors == [], f"Surface '{surface}' rejected"


def test_invalid_surface_rejected():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "nonexistent_surface", "title": "T", "entry": "t.html"}]})
    assert any("nonexistent_surface" in e for e in r.errors)


def test_surface_missing_title():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "entry": "t.html"}]})
    assert any("title" in e for e in r.errors)


def test_surface_missing_entry():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T"}]})
    assert any("entry" in e for e in r.errors)


def test_surface_valid_viewport():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html", "viewport": {"width": 400, "height": 300}}]})
    viewport_errors = [e for e in r.errors if "width" in e or "height" in e]
    assert viewport_errors == []


def test_surface_count():
    assert len(VALID_SURFACES) == 8


def test_all_surfaces_lowercase():
    for s in VALID_SURFACES:
        assert s == s.lower()
        assert "_" in s or s.isalpha()


def test_multiple_extensions():
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [
            {"surface": "dashboard_card", "title": "Card", "entry": "card.html"},
            {"surface": "cohort_tool", "title": "Tool", "entry": "tool.html"},
            {"surface": "settings_page", "title": "Settings", "entry": "settings.html"},
        ]})
    surface_errors = [e for e in r.errors if "surface" in e]
    assert surface_errors == []
