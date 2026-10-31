"""Parametrized viewport size validation tests."""

import pytest
from app.services.manifest_validator import validate_manifest

VALID_VIEWPORTS = [
    {"width": 100, "height": 100},
    {"width": 400, "height": 300},
    {"width": 800, "height": 600},
    {"width": 1920, "height": 1080},
    {"width": 100},
    {"height": 100},
]

INVALID_VIEWPORTS = [
    ({"width": 99}, "width too small"),
    ({"width": 1921}, "width too large"),
    ({"height": 99}, "height too small"),
    ({"height": 1081}, "height too large"),
    ({"width": 0}, "width zero"),
    ({"height": 0}, "height zero"),
    ({"width": -1}, "width negative"),
]

@pytest.mark.parametrize("viewport", VALID_VIEWPORTS)
def test_valid_viewport(viewport):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html", "viewport": viewport}]})
    vp_errors = [e for e in r.errors if "width" in e or "height" in e]
    assert vp_errors == [], f"Viewport {viewport} rejected"

@pytest.mark.parametrize("viewport,desc", INVALID_VIEWPORTS, ids=lambda x: x if isinstance(x, str) else "vp")
def test_invalid_viewport(viewport, desc):
    r = validate_manifest({"schema_version": "1.0", "app": {"name": "T"}, "permissions": ["extend:ui"],
        "ui_extensions": [{"surface": "dashboard_card", "title": "T", "entry": "t.html", "viewport": viewport}]})
    vp_errors = [e for e in r.errors if "width" in e or "height" in e]
    assert len(vp_errors) >= 1, f"Viewport {viewport} accepted ({desc})"
