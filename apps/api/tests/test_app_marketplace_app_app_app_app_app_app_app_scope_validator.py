from app.services.app_marketplace_app_app_app_app_app_app_app_scope_validator import validate_scopes, check_endpoint_access

def test_scopes():
    r = validate_scopes(granted_scopes=["write"], required_scope="read")
    assert r["allowed"]  # write includes read
    r2 = validate_scopes(granted_scopes=["read"], required_scope="write")
    assert not r2["allowed"]
    r3 = validate_scopes(granted_scopes=["admin"], required_scope="delete")
    assert r3["allowed"]

def test_endpoint():
    r = check_endpoint_access(scopes=["read"], method="GET", path="/api/users")
    assert r["allowed"]
    r2 = check_endpoint_access(scopes=["read"], method="POST", path="/api/users")
    assert not r2["allowed"]
    r3 = check_endpoint_access(scopes=["write"], method="DELETE", path="/api/users/1")
    assert not r3["allowed"]  # write doesn't include delete
