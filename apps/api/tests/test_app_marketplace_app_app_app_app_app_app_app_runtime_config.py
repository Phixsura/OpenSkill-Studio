from app.services.app_marketplace_app_app_app_app_app_app_app_runtime_config import RuntimeConfig

def test_set_get():
    rc = RuntimeConfig()
    rc.set("feature.dark_mode", "true", env="production")
    r = rc.get("feature.dark_mode")
    assert r["found"]
    assert r["value"] == "true"

def test_not_found():
    rc = RuntimeConfig()
    r = rc.get("missing", default="fallback")
    assert not r["found"]
    assert r["value"] == "fallback"

def test_get_all():
    rc = RuntimeConfig()
    rc.set("a", "1", env="prod")
    rc.set("b", "2", env="prod")
    rc.set("c", "3", env="staging")
    r = rc.get_all(env="prod")
    assert r["count"] == 2

def test_diff():
    rc = RuntimeConfig()
    rc.set("db_host", "prod-db", env="prod")
    rc.set("db_host", "stg-db", env="staging")
    rc.set("cache", "redis", env="prod")
    r = rc.diff("prod", "staging")
    assert r["total_diffs"] >= 1

def test_rollback():
    rc = RuntimeConfig()
    rc.set("flag", "v1")
    rc.set("flag", "v2")
    rc.rollback("flag")
    assert rc.get("flag")["value"] == "v1"

def test_audit():
    rc = RuntimeConfig()
    rc.set("x", "1")
    rc.set("x", "2")
    log = rc.audit_log()
    assert len(log) == 2
