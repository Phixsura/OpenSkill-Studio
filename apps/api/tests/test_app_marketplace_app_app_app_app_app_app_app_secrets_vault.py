from app.services.app_marketplace_app_app_app_app_app_app_app_secrets_vault import (
    store_secret, access_secret, rotate_secret, vault_summary, clear_vault,
)

def test_store_access():
    clear_vault()
    store_secret("DB_PASSWORD", "super_secret", "platform")
    r = access_secret("DB_PASSWORD", "api-service")
    assert r["found"]
    assert r["version"] == 1
    assert r["access_count"] == 1
    clear_vault()

def test_rotate():
    clear_vault()
    store_secret("API_KEY", "old_key")
    r = rotate_secret("API_KEY", "new_key")
    assert r["rotated"]
    assert r["new_version"] == 2
    clear_vault()

def test_summary():
    clear_vault()
    store_secret("a", "x")
    store_secret("b", "y")
    access_secret("a", "svc")
    s = vault_summary()
    assert s["total_secrets"] == 2
    assert s["total_accesses"] == 1
    clear_vault()
