from app.services.app_marketplace_app_app_app_app_app_app_app_token_introspect import introspect_token, check_token_permissions

def test_introspect():
    r = introspect_token({"sub": "user:123", "iss": "auth.example.com",
                            "scopes": ["read", "write"], "token_type": "bearer",
                            "exp": 9999999999, "active": True})
    assert r["active"]
    assert not r["expired"]
    assert r["scope_count"] == 2

def test_permissions():
    token = {"scopes": ["read", "write"]}
    r = check_token_permissions(token, ["read", "admin"])
    assert not r["authorized"]
    assert "admin" in r["missing"]
    r2 = check_token_permissions(token, ["read"])
    assert r2["authorized"]
