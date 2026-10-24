from app.services.app_marketplace_app_app_app_app_app_app_app_config_sync import ConfigSyncManager

def test_sync():
    cs = ConfigSyncManager()
    cs.set_config("prod", "db_host", "prod-db")
    cs.set_config("prod", "cache", "redis")
    r = cs.sync("prod", "staging")
    assert r["synced"] == 2
    d = cs.diff("prod", "staging")
    assert d["in_sync"]

def test_diff():
    cs = ConfigSyncManager()
    cs.set_config("prod", "a", "1")
    cs.set_config("staging", "a", "2")
    cs.set_config("staging", "b", "3")
    d = cs.diff("prod", "staging")
    assert not d["in_sync"]
    assert "a" in d["different"]
    assert "b" in d["only_in_staging"]
