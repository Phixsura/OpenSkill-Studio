from app.services.app_marketplace_app_app_app_app_app_app_app_secrets_vault import SecretsVault

def test_store_retrieve():
    sv = SecretsVault()
    sv.store("db_password", "super_secret_123", "admin")
    r = sv.retrieve("db_password", "api-service")
    assert r["found"]
    assert r["value"] == "super_secret_123"

def test_rotate():
    sv = SecretsVault()
    sv.store("api_key", "old_value", "admin")
    r = sv.rotate("api_key", "new_value", "admin")
    assert r["rotated"]
    assert r["version"] == 2
    r2 = sv.retrieve("api_key", "svc")
    assert r2["value"] == "new_value"

def test_audit():
    sv = SecretsVault()
    sv.store("k", "v", "admin")
    sv.retrieve("k", "svc1")
    sv.retrieve("k", "svc2")
    log = sv.audit_log()
    assert len(log) == 2
    assert sv.stats()["total_accesses"] == 2
