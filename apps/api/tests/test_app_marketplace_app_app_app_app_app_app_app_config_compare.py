from app.services.app_marketplace_app_app_app_app_app_app_app_config_compare import compare_configs

def test_compare():
    r = compare_configs({
        "dev": {"debug": True, "db_host": "localhost", "port": 8080},
        "prod": {"debug": False, "db_host": "prod-db", "port": 8080},
    })
    assert r["diff_count"] == 2  # debug, db_host
    assert r["same_count"] == 1  # port
    assert not r["identical"]

def test_identical():
    r = compare_configs({"a": {"x": 1}, "b": {"x": 1}})
    assert r["identical"]
