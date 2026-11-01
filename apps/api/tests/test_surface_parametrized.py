"""Parametrized tests for every UI surface."""

import pytest
from app.services.manifest_validator import VALID_SURFACES, validate_manifest

ALL_SURFACES = sorted(VALID_SURFACES)

@pytest.mark.parametrize("surface", ALL_SURFACES)
def test_surface_accepted(surface):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": surface, "title": "T", "entry": "t.html"}]})
    surface_errors = [e for e in r.errors if surface in e]
    assert surface_errors == []

@pytest.mark.parametrize("surface", ALL_SURFACES)
def test_surface_is_lowercase(surface):
    assert surface == surface.lower()

@pytest.mark.parametrize("surface", ALL_SURFACES)
def test_surface_is_snake_case(surface):
    assert all(c.isalpha() or c == "_" for c in surface)
