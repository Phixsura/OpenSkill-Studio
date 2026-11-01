"""App import validation edge cases."""

import pytest
from app.services.app_import import validate_import_data

NON_DICT_CASES = [None, 42, "string", []]

@pytest.mark.parametrize("data", NON_DICT_CASES, ids=lambda x: type(x).__name__)
def test_non_dict_raises(data):
    with pytest.raises((AttributeError, TypeError)):
        validate_import_data(data)

INVALID_DICTS = [
    ({}, "empty"),
    ({"app": None}, "app None"),
    ({"export_version": "1.0"}, "missing app"),
]

@pytest.mark.parametrize("data,desc", INVALID_DICTS, ids=lambda x: str(x)[:30])
def test_invalid_dict(data, desc):
    result = validate_import_data(data)
    assert not result.get("valid", True) or result.get("errors")

VALID = {
    "export_version": "1.0",
    "app": {"name": "Test", "slug": "test", "category": "automation"},
    "version": "1.0.0",
    "manifest": {
        "schema_version": "1.0",
        "app": {"name": "Test", "slug": "test", "version": "1.0.0", "category": "automation"},
        "permissions": ["read:cohorts"],
    },
}

def test_valid_no_errors():
    result = validate_import_data(VALID)
    assert result.get("valid") is True or not result.get("errors")
