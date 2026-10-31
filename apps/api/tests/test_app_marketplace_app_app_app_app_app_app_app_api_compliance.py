from app.services.app_marketplace_app_app_app_app_app_app_app_api_compliance import check_compliance, fleet_compliance

def test_compliant():
    r = check_compliance(
        {"path": "/api/v1/users", "auth_required": True, "uses_envelope": True},
        {"require_versioning": True, "require_auth": True, "snake_case_paths": True})
    assert r["compliant"]

def test_non_compliant():
    r = check_compliance(
        {"path": "/users", "auth_required": False},
        {"require_versioning": True, "require_auth": True})
    assert not r["compliant"]
    assert r["issue_count"] == 2

def test_fleet():
    r = fleet_compliance([
        {"path": "/api/v1/users", "auth_required": True},
        {"path": "/legacy", "auth_required": False},
    ], {"require_versioning": True, "require_auth": True})
    assert r["compliant"] == 1
    assert r["compliance_pct"] == 50.0
