from app.services.app_marketplace_app_app_app_app_app_app_app_oauth_scopes import validate_scopes, scope_diff, list_scopes

def test_validate():
    r = validate_scopes(["read:user", "write:apps", "fake:scope"])
    assert r["all_valid"] is False
    assert "fake:scope" in r["invalid"]
    assert "user" in r["categories"]

def test_diff():
    r = scope_diff(["read:user", "read:apps"], ["read:user", "write:apps", "admin"])
    assert "write:apps" in r["added"]
    assert "admin" in r["added"]
    assert "read:apps" in r["removed"]
    assert r["is_escalation"]

def test_list():
    user_scopes = list_scopes("user")
    assert len(user_scopes) == 2
    all_scopes = list_scopes()
    assert len(all_scopes) == 8
