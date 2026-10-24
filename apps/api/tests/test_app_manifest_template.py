"""Manifest template generator tests."""

import pytest
from app.services.app_manifest_template import get_template, fill_template, list_templates, TEMPLATES

CATEGORIES = list(TEMPLATES.keys())

@pytest.mark.parametrize("cat", CATEGORIES)
def test_get_template(cat):
    t = get_template(cat)
    assert t is not None
    assert t["schema_version"] == "1.0"
    assert t["app"]["category"] == cat

@pytest.mark.parametrize("cat", CATEGORIES)
def test_template_has_permissions(cat):
    t = get_template(cat)
    assert "permissions" in t
    assert len(t["permissions"]) > 0

@pytest.mark.parametrize("cat", CATEGORIES)
def test_fill_template(cat):
    t = fill_template(cat, name="My App", slug="my-app")
    assert t["app"]["name"] == "My App"
    assert t["app"]["slug"] == "my-app"

def test_get_unknown_returns_none():
    assert get_template("unknown_category") is None

def test_fill_unknown_returns_none():
    assert fill_template("unknown", name="X", slug="x") is None

def test_list_templates():
    result = list_templates()
    assert len(result) == len(TEMPLATES)
    assert all("category" in t for t in result)

def test_templates_independent():
    t1 = get_template("connector")
    t2 = get_template("connector")
    t1["app"]["name"] = "modified"
    assert t2["app"]["name"] == ""  # Deep copy

def test_connector_has_sandbox():
    t = get_template("connector")
    assert "sandbox" in t

def test_ui_extension_has_extensions():
    t = get_template("ui_extension")
    assert "ui_extensions" in t
    assert len(t["ui_extensions"]) > 0
