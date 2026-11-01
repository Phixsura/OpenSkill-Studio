"""App dependency checker tests."""

import pytest
from app.services.app_dependency import check_uninstall_impact, check_revoke_impact, validate_dependencies

def test_uninstall_safe():
    result = check_uninstall_impact(app_id="a1", app_event_types=["custom.event"], all_subscriptions=[])
    assert result["safe"] is True

def test_uninstall_impact():
    subs = [
        {"app_id": "a2", "event_type": "submission.completed", "installation_id": "i2"},
    ]
    result = check_uninstall_impact(app_id="a1", app_event_types=["submission.completed"], all_subscriptions=subs)
    assert result["safe"] is False
    assert "a2" in result["affected_apps"]

def test_uninstall_skips_own():
    subs = [{"app_id": "a1", "event_type": "submission.completed", "installation_id": "i1"}]
    result = check_uninstall_impact(app_id="a1", app_event_types=["submission.completed"], all_subscriptions=subs)
    assert result["safe"] is True

def test_revoke_safe():
    result = check_revoke_impact(app_id="a1", active_installations=[])
    assert result["safe"] is True

def test_revoke_impact():
    installs = [
        {"app_id": "a1", "org_id": "o1", "status": "active"},
        {"app_id": "a1", "org_id": "o2", "status": "active"},
        {"app_id": "a2", "org_id": "o1", "status": "active"},
    ]
    result = check_revoke_impact(app_id="a1", active_installations=installs)
    assert result["affected_installations"] == 2
    assert result["total_orgs"] == 2

def test_validate_deps_satisfied():
    result = validate_dependencies(required_permissions=["read:cohorts"], granted_permissions=["read:cohorts", "write:projects"])
    assert result["satisfied"] is True

def test_validate_deps_missing():
    result = validate_dependencies(required_permissions=["read:cohorts", "write:cohorts"], granted_permissions=["read:cohorts"])
    assert result["satisfied"] is False
    assert "write:cohorts" in result["missing"]
