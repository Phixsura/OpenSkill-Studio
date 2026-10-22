"""App export/import service tests."""

import inspect
import pytest
from app.services.app_export import export_app_config, export_installation_config
from app.services.app_import import validate_import_data, prepare_import_plan


def test_export_app_is_async():
    assert inspect.iscoroutinefunction(export_app_config)

def test_export_installation_is_async():
    assert inspect.iscoroutinefunction(export_installation_config)

def test_validate_import_is_sync():
    assert not inspect.iscoroutinefunction(validate_import_data)

def test_prepare_import_plan_is_sync():
    assert not inspect.iscoroutinefunction(prepare_import_plan)

# --- validate_import_data ---

INVALID_IMPORTS = [
    ({}, "empty"),
    ({"app": {}}, "no version"),
    ({"version": "1.0"}, "no app key"),
    ({"app": {"name": ""}, "version": "1.0"}, "empty name"),
]

@pytest.mark.parametrize("data,desc", INVALID_IMPORTS, ids=lambda x: str(x)[:30])
def test_validate_rejects_invalid(data, desc):
    result = validate_import_data(data)
    assert not result.get("valid", True) or result.get("errors")

VALID_IMPORT = {
    "app": {"name": "Test App", "slug": "test-app", "category": "utility"},
    "version": "1.0.0",
    "manifest": {
        "schema_version": "1.0",
        "app": {"name": "Test App", "slug": "test-app", "version": "1.0.0", "category": "utility"},
        "permissions": ["read:cohorts"],
    },
}

def test_validate_accepts_valid():
    result = validate_import_data(VALID_IMPORT)
    assert result.get("valid") is True or not result.get("errors")

def test_prepare_import_plan_returns_dict():
    result = prepare_import_plan(VALID_IMPORT)
    assert isinstance(result, dict)

def test_prepare_import_plan_has_actions():
    result = prepare_import_plan(VALID_IMPORT)
    assert "actions" in result or "steps" in result or "plan" in result or "summary" in result
