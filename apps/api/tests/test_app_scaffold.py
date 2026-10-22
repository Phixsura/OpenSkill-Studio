"""App scaffold generator tests."""

import pytest
from app.services.app_scaffold import generate_scaffold, list_scaffold_types, FILE_TEMPLATES

CATEGORIES = list(FILE_TEMPLATES.keys())

@pytest.mark.parametrize("cat", CATEGORIES)
def test_generate_returns_files(cat):
    files = generate_scaffold(name="Test App", slug="test-app", category=cat)
    assert isinstance(files, dict)
    assert len(files) > 0

@pytest.mark.parametrize("cat", CATEGORIES)
def test_files_are_strings(cat):
    files = generate_scaffold(name="X", slug="x", category=cat)
    for path, content in files.items():
        assert isinstance(path, str)
        assert isinstance(content, str)

def test_connector_has_src():
    files = generate_scaffold(name="My Conn", slug="my-conn", category="connector")
    assert any("src/" in p for p in files.keys())

def test_connector_has_tests():
    files = generate_scaffold(name="My Conn", slug="my-conn", category="connector")
    assert any("test" in p for p in files.keys())

def test_name_interpolated():
    files = generate_scaffold(name="Cool App", slug="cool-app", category="connector")
    readme = files.get("README.md", "")
    assert "Cool App" in readme

def test_list_scaffold_types():
    types = list_scaffold_types()
    assert len(types) == len(FILE_TEMPLATES)
    assert all("category" in t for t in types)

def test_unknown_category_defaults():
    files = generate_scaffold(name="X", slug="x", category="unknown_type")
    assert len(files) > 0  # Falls back to connector
