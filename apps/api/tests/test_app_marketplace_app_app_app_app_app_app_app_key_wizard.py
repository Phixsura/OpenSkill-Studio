from app.services.app_marketplace_app_app_app_app_app_app_app_key_wizard import create_key, list_scopes

def test_create():
    r = create_key(name="CI Key", scopes=["read:apps", "deploy"], expires_days=90)
    assert r["key"].startswith("sk_live_")
    assert r["scope_count"] == 2
    assert r["max_risk"] == "high"
    assert r["warning"] is None

def test_admin():
    r = create_key(name="Admin", scopes=["admin"])
    assert r["max_risk"] == "critical"
    assert r["warning"] is not None

def test_scopes():
    assert len(list_scopes()) == 6
