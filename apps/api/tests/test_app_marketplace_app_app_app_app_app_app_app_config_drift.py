from app.services.app_marketplace_app_app_app_app_app_app_app_config_drift import detect_drift, compare_envs

def test_no_drift():
    r = detect_drift({"a": "1", "b": "2"}, {"a": "1", "b": "2"})
    assert not r["drifted"]
    assert r["severity"] == "ok"

def test_drift():
    r = detect_drift({"a": "1", "b": "2"}, {"a": "X", "c": "3"})
    assert r["drifted"]
    assert "b" in r["missing"]
    assert "c" in r["extra"]
    assert r["changed"][0]["key"] == "a"
    assert r["severity"] == "critical"

def test_compare_envs():
    r = compare_envs({
        "prod": {"db": "prod-db", "cache": "redis"},
        "staging": {"db": "stg-db", "cache": "redis"},
        "dev": {"db": "dev-db"},
    }, baseline="prod")
    assert r["drifted"] == 2
    assert r["total_envs"] == 2
