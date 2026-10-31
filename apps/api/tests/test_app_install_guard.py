"""App install guard tests."""
from app.services.app_install_guard import pre_install_check

def test_allowed():
    r = pre_install_check(app_status="published", org_app_count=5)
    assert r["allowed"] is True

def test_not_published():
    r = pre_install_check(app_status="draft", org_app_count=0)
    assert r["allowed"] is False

def test_limit_reached():
    r = pre_install_check(app_status="published", org_app_count=50, max_apps_per_org=50)
    assert r["allowed"] is False

def test_blocked_category():
    r = pre_install_check(app_status="published", org_app_count=0, blocked_categories=["connector"], app_category="connector")
    assert r["allowed"] is False

def test_near_limit_warning():
    r = pre_install_check(app_status="published", org_app_count=42, max_apps_per_org=50)
    assert r["allowed"] is True
    assert len(r["warnings"]) > 0
