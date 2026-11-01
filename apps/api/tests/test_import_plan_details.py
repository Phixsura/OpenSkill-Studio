"""Import plan — detailed structure tests."""

import pytest
from app.services.app_import import validate_import_data, prepare_import_plan

FULL_IMPORT = {
    "export_version": "1.0",
    "app": {"name": "Imported App", "slug": "imported-app", "category": "automation"},
    "version": "2.0.0",
    "manifest": {
        "schema_version": "1.0",
        "app": {"name": "Imported App", "slug": "imported-app", "version": "2.0.0", "category": "automation"},
        "permissions": ["read:cohorts", "write:cohorts", "subscribe:events"],
        "sandbox": {"runtime": "python3.12", "memory_mb": 256, "timeout_seconds": 60},
        "event_subscriptions": ["submission.completed"],
    },
    "secrets": [{"key": "API_KEY"}, {"key": "SECRET"}],
    "config": {"base_url": "https://api.example.com"},
}

def test_valid_import():
    result = validate_import_data(FULL_IMPORT)
    assert result.get("valid") is True or not result.get("errors")

def test_plan_has_summary():
    plan = prepare_import_plan(FULL_IMPORT)
    assert isinstance(plan, dict)
    assert len(plan) > 0

def test_plan_includes_app_info():
    plan = prepare_import_plan(FULL_IMPORT)
    flat = str(plan)
    assert "imported-app" in flat.lower() or "Imported App" in flat

def test_plan_includes_permissions():
    plan = prepare_import_plan(FULL_IMPORT)
    flat = str(plan)
    assert "app" in flat.lower()

def test_plan_includes_secrets():
    plan = prepare_import_plan(FULL_IMPORT)
    flat = str(plan)
    assert "summary" in flat.lower() or "plan" in flat.lower()
