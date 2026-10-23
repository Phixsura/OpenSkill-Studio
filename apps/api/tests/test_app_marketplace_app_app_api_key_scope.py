from app.services.app_marketplace_app_app_api_key_scope import validate_scopes, get_minimal_scopes

def test_valid():
    r = validate_scopes(requested=["apps:read", "analytics:read"])
    assert r["all_valid"]
    assert r["max_risk"] == "low"
    assert not r["needs_approval"]

def test_high_risk():
    r = validate_scopes(requested=["apps:read", "admin:all"])
    assert r["max_risk"] == "critical"
    assert r["needs_approval"]

def test_invalid():
    r = validate_scopes(requested=["apps:read", "magic:power"])
    assert not r["all_valid"]
    assert "magic:power" in r["invalid_scopes"]

def test_minimal():
    r = get_minimal_scopes(operations=["list_apps", "view_analytics"])
    assert "apps:read" in r["minimal_scopes"]
    assert "analytics:read" in r["minimal_scopes"]
    assert r["scope_count"] == 2
