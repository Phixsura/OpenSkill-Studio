from app.services.app_developer_api_key_permissions import validate_key_scopes, check_key_access

def test_valid():
    r = validate_key_scopes(["read:cohorts"], ["read:cohorts", "write:projects"])
    assert r["valid"] is True

def test_denied():
    r = validate_key_scopes(["admin:all"], ["read:cohorts"])
    assert r["valid"] is False
    assert "admin:all" in r["denied"]

def test_check_access():
    assert check_key_access(["read:cohorts", "write:projects"], "read:cohorts") is True
    assert check_key_access(["read:cohorts"], "write:projects") is False
