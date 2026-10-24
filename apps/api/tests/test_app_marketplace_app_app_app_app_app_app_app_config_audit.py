from app.services.app_marketplace_app_app_app_app_app_app_app_config_audit import ConfigAuditor

def test_audit():
    ca = ConfigAuditor()
    ca.record_change("db_host", "old-db", "new-db", "alice", "prod")
    ca.record_change("cache_size", "100", "200", "bob", "staging")
    ca.record_change("db_host", "new-db", "newer-db", "alice", "prod")
    r = ca.query(key="db_host")
    assert len(r) == 2
    r2 = ca.query(changed_by="bob")
    assert len(r2) == 1
    s = ca.stats()
    assert s["total_changes"] == 3
    assert s["by_env"]["prod"] == 2
