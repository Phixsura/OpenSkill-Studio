from app.services.app_marketplace_app_oauth_scope_manager import validate_scopes, group_scopes_by_category

def test_valid():
    r = validate_scopes(requested=["read:profile", "read:apps"])
    assert r["all_valid"]
    assert r["max_risk"] == "low"
    assert not r["requires_admin_consent"]

def test_high_risk():
    r = validate_scopes(requested=["read:profile", "admin:org"])
    assert r["max_risk"] == "critical"
    assert r["requires_admin_consent"]

def test_invalid():
    r = validate_scopes(requested=["read:profile", "hack:everything"])
    assert not r["all_valid"]
    assert "hack:everything" in r["invalid_scopes"]

def test_group():
    r = group_scopes_by_category(scopes=["read:profile", "write:profile", "read:apps"])
    assert r["category_count"] == 2
