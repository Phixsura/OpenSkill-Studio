from app.services.app_marketplace_app_config_diff import diff_configs

def test_diff():
    a = {"DB_HOST": "localhost", "LOG_LEVEL": "debug", "SECRET": "dev_secret"}
    b = {"DB_HOST": "prod-db.example.com", "LOG_LEVEL": "info", "REDIS_URL": "redis://prod"}
    r = diff_configs(env_a="staging", config_a=a, env_b="production", config_b=b)
    assert r["diff_count"] == 4  # 2 changed + 1 removed + 1 added
    assert r["same_count"] == 0
    changed = [d for d in r["diffs"] if d["type"] == "changed"]
    assert len(changed) == 2

def test_identical():
    cfg = {"A": "1", "B": "2"}
    r = diff_configs(env_a="dev", config_a=cfg, env_b="staging", config_b=cfg)
    assert r["diff_count"] == 0
    assert r["drift_pct"] == 0
