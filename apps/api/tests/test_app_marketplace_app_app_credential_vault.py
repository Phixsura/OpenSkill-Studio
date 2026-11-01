from app.services.app_marketplace_app_app_credential_vault import store_credential, check_rotation

def test_store():
    r = store_credential(name="DB_PASSWORD", value="super_secret_123", rotation_days=30)
    assert r["id"].startswith("cred_")
    assert r["name"] == "DB_PASSWORD"
    assert "•" in r["preview"]
    assert r["status"] == "active"

def test_rotation_expired():
    creds = [{"name": "OLD_KEY", "expires_at": "2020-01-01T00:00:00+00:00"}]
    r = check_rotation(credentials=creds)
    assert r["needs_attention"]
    assert "OLD_KEY" in r["expired"]

def test_rotation_ok():
    creds = [{"name": "NEW_KEY", "expires_at": "2099-01-01T00:00:00+00:00"}]
    r = check_rotation(credentials=creds)
    assert not r["needs_attention"]
