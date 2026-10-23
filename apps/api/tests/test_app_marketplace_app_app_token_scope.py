from app.services.app_marketplace_app_app_token_scope import validate_scopes, list_scopes

def test_valid_scopes():
    r = validate_scopes(requested=["read:apps", "read:analytics"])
    assert r["all_valid"]
    assert not r["has_dangerous"]

def test_dangerous():
    r = validate_scopes(requested=["admin", "read:apps"])
    assert r["has_dangerous"]
    assert "admin" in r["dangerous"]

def test_invalid():
    r = validate_scopes(requested=["read:apps", "fake:scope"])
    assert not r["all_valid"]
    assert "fake:scope" in r["invalid"]

def test_list():
    r = list_scopes()
    assert r["total"] == 7
    r2 = list_scopes(category="Apps")
    assert r2["total"] == 3
