"""Parametrized import validation tests."""

import pytest
from app.services.app_import import validate_import_data

VALID_IMPORTS = [
    {"export_version": "1.0", "app": {"name": "A", "slug": "a"}, "versions": []},
    {"export_version": "1.0", "app": {"name": "B", "slug": "b"}, "versions": [{"version": "1.0.0", "content_hash": "a" * 64}]},
    {"export_version": "1.0", "app": {"name": "C", "slug": "c"}, "versions": [], "ui_extensions": []},
]

INVALID_IMPORTS = [
    ({}, "no app"),
    ({"export_version": "1.0"}, "missing app"),
    ({"export_version": "1.0", "app": {"slug": "x"}}, "missing name"),
    ({"export_version": "1.0", "app": {"name": "X"}}, "missing slug"),
    ({"export_version": "1.0", "app": {"name": "X", "slug": "x"}, "versions": "str"}, "non-list versions"),
]

@pytest.mark.parametrize("data", VALID_IMPORTS)
def test_valid_import(data):
    result = validate_import_data(data)
    assert result["valid"] is True

@pytest.mark.parametrize("data,desc", INVALID_IMPORTS, ids=lambda x: x if isinstance(x, str) else "data")
def test_invalid_import(data, desc):
    result = validate_import_data(data)
    assert result["valid"] is False or len(result["errors"]) > 0, f"Expected invalid for: {desc}"
