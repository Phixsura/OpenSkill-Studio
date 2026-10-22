"""App import validation edge cases."""

import pytest
from app.services.app_import import validate_import_data

INVALID_CASES = [
    (None, "none input"),
    (42, "not a dict"),
    ("string", "string input"),
    ([], "list input"),
    ({}, "empty dict"),
    ({"app": None}, "app is None"),
    ({"app": {"name": "X"}, "version": None}, "version None"),
]

@pytest.mark.parametrize("data,desc", INVALID_CASES, ids=lambda x: str(x)[:30])
def test_invalid_import_data(data, desc):
    result = validate_import_data(data)
    assert not result.get("valid", True) or result.get("errors")

VALID = {
    "app": {"name": "Test", "slug": "test", "category": "automation"},
    "version": "1.0.0",
    "manifest": {
        "schema_version": "1.0",
        "app": {"name": "Test", "slug": "test", "version": "1.0.0", "category": "automation"},
        "permissions": ["read:cohorts"],
    },
}

def test_valid_returns_no_errors():
    result = validate_import_data(VALID)
    assert result.get("valid") is True or not result.get("errors")

def test_import_result_is_dict():
    result = validate_import_data(VALID)
    assert isinstance(result, dict)
